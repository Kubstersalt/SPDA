from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

#Load in environment variables
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

#Creates object which automatically applies creates and applies token for general search
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
#Same idea but for specific user requests
scope = "user-library-read"
user = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_artist_albums(spotify, artist_uri):
    results = spotify.artist_albums(artist_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])
    
    for album in albums:
        print(album['name'])

def get_user_saved_tracks(user):
    results = user.current_user_saved_tracks(limit=50)
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])

get_artist_albums(spotify, "spotify:artist:1oPRcJUkloHaRLYx0olBLJ")
get_user_saved_tracks(user)