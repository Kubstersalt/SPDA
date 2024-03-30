#Currently working on this
from dotenv import load_dotenv
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import time
from datetime import datetime, timezone
from dateutil.parser import isoparse
import csv

#Load in environment variables
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

#Creates object which automatically creates and applies token for general search
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
#Same idea but for specific user requests
scope = "user-read-recently-played"
user = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_recent(user, days):
    #Timestamp to start measuring from
    timestamp_today = (int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())-60*60*2)
    timestamp_adjusted = timestamp_today - (days*24*60*60)
    batch = user.current_user_recently_played(after=timestamp_adjusted*1000)
    size = len(batch["items"])
    print(f"Batch size: {size}")
    name_last = batch["items"][size-1]["track"]["name"]
    
    latest_date = int(isoparse(batch["items"][size-1]["played_at"]).timestamp())
    with open("recently_listened.json", "w") as outfile:
        json.dump(batch, outfile)
    
    header = ["datetime", "name"]
    content = []
    for item in batch["items"]:
        date_time = datetime.fromtimestamp(int(isoparse(item["played_at"]).timestamp()))
        name = item["track"]["name"]
        content.append([date_time, name])

    with open("batch.csv", "w", newline="") as overview:
        writer = csv.writer(overview)
        writer.writerow(header)
        for pair in content:
            writer.writerow(pair)

    print(f"Start today from: {datetime.fromtimestamp(timestamp_today)}")
    print(f"Starting from: {datetime.fromtimestamp(timestamp_adjusted)}")
    print(f"Last in batch: {latest_date}")
    print(f"Last song: {name_last}")
    print(timestamp_today)
    print(latest_date)

def main():
    days = int(input("How many days do you wanna go back? (0 is just today)"))
    get_recent(user, days)
main()