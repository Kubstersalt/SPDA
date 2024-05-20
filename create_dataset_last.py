from dotenv import load_dotenv
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import time
from datetime import datetime, timezone
from dateutil.parser import isoparse
import csv
import requests
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

#Load environment variables
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
last_key = os.getenv("LAST_KEY")
last_secret = os.getenv("LAST_SECRET")
last_user = os.getenv("LAST_USERNAME")

#Creates object which automatically creates and applies token for general search
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
#Same idea but for specific user requests
scope = "user-read-recently-played"
user = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

pause_duration = 0.1

url = 'https://ws.audioscrobbler.com/2.0/?method=user.get{}&user={}&api_key={}&limit={}&extended={}&page={}&format=json'
limit = 200 #api lets you retrieve up to 200 records per call
extended = 0 #api lets you retrieve extended data for each track, 0=no, 1=yes
page = 1 #page of results to start retrieving at

def get_scrobbles(method='recenttracks', username=last_user, key=last_key, limit=200, extended=0, page=1, pages=0):
    '''
    method: api method
    username/key: api credentials
    limit: api lets you retrieve up to 200 records per call
    extended: api lets you retrieve extended data for each track, 0=no, 1=yes
    page: page of results to start retrieving at
    pages: how many pages of results to retrieve. if 0, get as many as api can return.
    '''
    # initialize url and lists to contain response fields
    url = 'https://ws.audioscrobbler.com/2.0/?method=user.get{}&user={}&api_key={}&limit={}&extended={}&page={}&format=json'
    responses = []
    artist_names = []
    artist_mbids = []
    album_names = []
    album_mbids = []
    track_names = []
    track_mbids = []
    timestamps = []
    
    # make first request, just to get the total number of pages
    request_url = url.format(method, last_user, last_key, limit, extended, page)
    response = requests.get(request_url).json()
    total_pages = int(response[method]['@attr']['totalPages'])
    if pages > 0:
        total_pages = min([total_pages, pages])
        
    print('{} total pages to retrieve'.format(total_pages))
    
    # request each page of data one at a time
    for page in range(1, int(total_pages) + 1, 1):
        time.sleep(pause_duration)
        request_url = url.format(method, last_user, last_key, limit, extended, page)
        responses.append(requests.get(request_url))
        print(f"{page}/{total_pages}")
    
    # parse the fields out of each scrobble in each page (aka response) of scrobbles
    for response in responses:
        scrobbles = response.json()
        for scrobble in scrobbles[method]['track']:
            # only retain completed scrobbles (aka, with timestamp and not 'now playing')
            if 'date' in scrobble.keys():
                artist_names.append(scrobble['artist']['#text'])
                artist_mbids.append(scrobble['artist']['mbid'])
                album_names.append(scrobble['album']['#text'])
                album_mbids.append(scrobble['album']['mbid'])
                track_names.append(scrobble['name'])
                track_mbids.append(scrobble['mbid'])
                timestamps.append(scrobble['date']['uts'])
                
    # create and populate a dataframe to contain the data
    df = pd.DataFrame()
    df['artist'] = artist_names
    df['artist_mbid'] = artist_mbids
    df['album'] = album_names
    df['album_mbid'] = album_mbids
    df['track'] = track_names
    df['track_mbid'] = track_mbids
    df['timestamp'] = timestamps
    df['datetime'] = pd.to_datetime((df['timestamp']).astype(int)+2*60*60, unit='s')
    
    return df

def add_spotify_data():
    '''
    collect all data
    rows: the amount of rows (head) from the lastfm_scrobbles file that you want corresponding spotify data for.
    '''

    def get_features(response, index, skip):
        '''
        Extract song's features from spotify API request response
        response: result of API request
        skip: if you want to skip the song and enter empty values in dataframe
        '''
        if skip:
            df["danceability"][index] = "-"
            df["energy"][index] = "-"
            df["speechiness"][index] = "-"
            df["acousticness"][index] = "-"
            df["instrumentalness"][index] = "-"
            df["liveness"][index] = "-"
            df["valence"][index] = "-"
            df["ids"][index] = "-"
            df["tempo"][index] = "-"
            df["duration"][index] = "-"
            df["time_signature"][index] = "-"
            df["key"][index] = "-"
            df["loudness"][index] = "-"
            df["mode"][index] = "-"

        else:
            track_id = response["tracks"]["items"][0]["id"]
            features = spotify.audio_features(track_id)[0]
            if features:
                df["danceability"][index] = features["danceability"]
                df["energy"][index] = features["energy"]
                df["speechiness"][index] = features["speechiness"]
                df["acousticness"][index] = features["acousticness"]
                df["instrumentalness"][index] = features["instrumentalness"]
                df["liveness"][index] = features["liveness"]
                df["valence"][index] = features["valence"]
                df["ids"][index] = track_id
                df["tempo"][index] = features["tempo"]
                df["duration"][index] = features["duration_ms"]
                df["time_signature"][index] = features["time_signature"]
                df["key"][index] = features["key"]
                df["loudness"][index] = features["loudness"]
                df["mode"][index] = features["mode"]
            else:
                df["error"][index] = "C"
                get_features(response, index, True)
        return
    
    #check if lastfm_scrobbles.csv exists to load in
    try:
        #load in lastfm_scrobbles.csv
        df = pd.read_csv('datasets/tracks_data.csv')
        print("Loaded previous tracks data file succesfully")
    except:
        print("tracks_data.csv does not exist, trying to create it from lastfm_scrobbles.csv")
        df = pd.read_csv('datasets/lastfm_scrobbles.csv')
        placeholder_list = [None for _ in range(len(df))]
        df["danceability"] = placeholder_list
        df["energy"] = placeholder_list
        df["speechiness"] = placeholder_list
        df["acousticness"] = placeholder_list
        df["instrumentalness"] = placeholder_list
        df["liveness"] = placeholder_list
        df["valence"] = placeholder_list
        df["ids"] = placeholder_list
        df["tempo"] = placeholder_list
        df["duration"] = placeholder_list
        df["time_signature"] = placeholder_list
        df["loudness"] = placeholder_list
        df["key"] = placeholder_list
        df["mode"] = placeholder_list
        df["error"] = placeholder_list

    #Now start by finding where to begin
    i=0
    for value in df["error"]:
        if (isinstance(value, str)==False):
            start_index = i
            break
        else:
            i+=1
    print(f"starting at {start_index}")

    #Continue at start_index, replace entries at row-index of dataframe with retrieved data
    pause_duration = 0.00125
    start_time = time.time()
    for index in range(start_index, len(df)):
        time.sleep(pause_duration)

        track = df["track"][index]
        artist = df["artist"][index]

        query = "artist:" + artist + " track:" + track

        response = user.search(q=query, type='track')
        if response["tracks"]["items"]:
            get_features(response, index, False)
            df["error"][index] = "-"

        else:
            #print("Error: removing apostrophes from query")
            df["error"][index] = "A"
            track = track.replace("'","")
            query = "artist:" + artist + " track:" + track
            response = user.search(q=query, type='track')

            if response["tracks"]["items"]:
                get_features(response, index, False)

            else:
                #print("Error: skipped")
                df["error"][index] = "B"
                get_features(response, index, True)

        #Overwrite tracks_data.csv every n amount of indices
        if ((index+1)%500==0):
            end_time = time.time()
            df.to_csv('datasets/tracks_data.csv', index=None, encoding='utf-8')
            print(f"{index+1}/{len(df)} done!")
            print(f"It took {end_time - start_time} ms")
            #pause_duration = pause_duration/2
            print(f"New pause duration to test: {pause_duration}")
            print("Saved progress! Continuing...")
            start_time = time.time()
    
    #final save
    df.to_csv('datasets/tracks_data.csv', index=None, encoding='utf-8')

    return

def check_validity():

    return

def main():
    cont = True
    while cont:
        select = int(input("Select what you want to do:\n1. Retrieve Last.FM scrobbles in CSV\n2. Collect spotify metrics for entire scrobbles dataset\n3. Check Validity\n4. Quit\n"))
        if select==1:
            scrobbles = get_scrobbles(pages=0)
            scrobbles.to_csv('datasets/lastfm_scrobbles.csv', index=None, encoding='utf-8')
            print('{:,} total rows'.format(len(scrobbles)))
        elif select==2:
            add_spotify_data()
            #added_data.to_csv('datasets/tracks_data.csv', index=None, encoding='utf-8')
            #print('{:,} total rows'.format(len(added_data)))
        elif select==3:
            check_validity()
        elif select==4:
            print("Bye Bye")
            cont = False

main()