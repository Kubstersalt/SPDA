#Currently working on this
from dotenv import load_dotenv
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import time

#Load in environment variables
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

#Creates object which automatically applies creates and applies token for general search
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
#Same idea but for specific user requests
scope = "user-read-recently-played"
user = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_recent(user):
    tracks = user.current_user_recently_played(limit=10)
    print(tracks["items"][0]["track"]["id"])
    with open("recently_listened", "w") as outfile:
        json.dump(tracks, outfile)

def main():
    get_recent(user)

main()