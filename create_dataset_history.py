#Currently working on this
from dotenv import load_dotenv
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import time
from datetime import datetime, timezone
from dateutil.parser import isoparse

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
    #Very ugly timezone adjustment
    timestamp = (int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())-60*60*2)
    tracks = user.current_user_recently_played(after=timestamp*1000)
    size = len(tracks["items"])
    print(f"Batch size: {size}")
    name_last = tracks["items"][size-1]["track"]["name"]
    
    latest_date = int(isoparse(tracks["items"][size-1]["played_at"]).timestamp())
    with open("recently_listened", "w") as outfile:
        json.dump(tracks, outfile)
    print(f"Starting from: {datetime.fromtimestamp(timestamp)}")
    print(f"Last in batch: {datetime.fromtimestamp(latest_date)}")
    print(f"Last song: {name_last}")
    print(timestamp)

def main():
    get_recent(user)
main()