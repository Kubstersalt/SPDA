from dotenv import load_dotenv
import os
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
scope = "user-read-currently-playing"
user = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def update(current_id):
    track = user.current_user_playing_track()
    if track != None:
    #In case user skipped manually, interval between stopping and starting results in error
        if track["item"] != None:
            track_id = track["item"]["id"]
            #If new track_id, print new song and its features
            if track_id != current_id:
                track_name = track["item"]["name"]
                features = spotify.audio_features(track_id)[0]
                acousticness = features["acousticness"]
                danceability = features["danceability"]
                energy = features["energy"]
                instrumentalness = features["instrumentalness"]
                liveness = features["liveness"]
                speechiness = features["speechiness"]
                valence = features["valence"]
                print(f"Name: {track_name}\n acousticness: {acousticness}\n danceability: {danceability}\n energy: {energy}\n instrumentalness: {instrumentalness}\n liveness: {liveness}\n speechiness: {speechiness}\n Valence: {valence}")
                print(features)
                return(track_id)
    return current_id

def main():
    current_id = None
    
    while True:
        current_id = update(current_id)
        time.sleep(1)

main()