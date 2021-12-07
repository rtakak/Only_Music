DEBUG = False
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

scopes = ["https://www.googleapis.com/auth/youtube"]
sp_scopes = "playlist-modify-public" + ",user-read-private"
KEY = "#"
SPOTIPY_CLIENT_ID = '#'
SPOTIPY_CLIENT_SECRET = '#'
SPOTIPY_REDIRECT_URI = 'http://localhost:9090'


def create_spotify_list(sp, title, description):
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user_id, title, description=description)
    return playlist['id']


def create_playlist(youtube, title, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": [
                    "Music Only",
                    "API call"
                ],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = request.execute()
    return response["id"]


def add_video_to_playlist(youtube, music, playlistID):
    for videoID in music:
        add_video_request = youtube.playlistItems().insert(
            part="snippet",
            body={
                'snippet': {
                    'playlistId': playlistID,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': videoID[1]
                    }
                    # 'position': 0
                }
            }
        )
        response = add_video_request.execute()
        print(f"{videoID[0]} added to playlist.")
        if DEBUG:
            print(response)


def find_spotify_track_ids(sp, items):
    track_ids = []
    none = []
    for item in items:
        track_id = sp.search(q='track:' + item, type='track')
        if track_id['tracks']['items']:
            track_id = track_id['tracks']['items'][0]['id']
            track_ids.append(track_id)
        else:
            none.append(item)
    print(none)
    return track_ids


def add_tracks_to_spotify(sp, playlist, items):
    pl_id = create_spotify_list(sp, playlist[1], playlist[2])
    tracks = find_spotify_track_ids(sp, items)
    sp.playlist_add_items(pl_id, tracks)
    print("bitti")


def get_playlist_from_URl(youtube):
    while True:
        try:
            url = input("Playlist URL: ")
            pl_id = url.split("list=", 1)[1]
            if DEBUG:
                print(pl_id)
            response = youtube.playlists().list(
                part="snippet",
                id=pl_id
            ).execute()
            playlist_name = response['items'][0]['snippet']['title']
            playlist_description = response['items'][0]['snippet']['description']
            print(playlist_name, "-", playlist_description)
        except IndexError:
            print("Invalid URL, try again! ")
            continue
        else:
            return pl_id, playlist_name, playlist_description


def get_playlist_items(youtube, pl_id):
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=pl_id,
        part="snippet"
    )
    musics = []
    while playlistitems_list_request:
        # 1 quota per item
        playlistitems_list_response = playlistitems_list_request.execute()

        for playlist_item in playlistitems_list_response["items"]:
            title = playlist_item["snippet"]["title"]
            musics.append(title)

        playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)
    print(musics)
    return musics


def setup():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "#"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials, developerKey=KEY)

    auth = SpotifyOAuth(scope=sp_scopes, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI)
    sp = spotipy.Spotify(auth_manager=auth)
    return youtube, sp


def main():
    youtube, sp = setup()
    playlist = get_playlist_from_URl(youtube)
    items = get_playlist_items(youtube, playlist[0])
    add_tracks_to_spotify(sp, playlist, items)



main()

