import requests
import os
from dotenv import load_dotenv
import base64
from pathlib import Path

'''
SPOTIFY CONSTANTS
'''
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Spotify API URLs
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"

def get_access_token():
    # Create the Base64 encoded authorization header
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth_str.encode()).decode()

    # Set up the request headers and data
    auth_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + auth_base64
    }
    data = {
        'grant_type': 'client_credentials'
    }

    # Make the POST request to get the token
    auth_response = requests.post(auth_url, headers=headers, data=data)

    # Raise exception if connection is unsuccessful
    auth_response.raise_for_status()

    response = auth_response.json()
    
    return response['access_token']


def get_spotify_song(query):
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": query, "type": "track", "limit": 1}

    # Perform search query to Spotify API
    response = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["tracks"]["items"]:
            track = data["tracks"]["items"][0]
            artist = track["artists"][0]["name"]
            track_name = track["name"]
            return artist, track_name
    else:
        print("Error:", response.json())
        return None