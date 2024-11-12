from functools import lru_cache
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Final
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.parse

'''
YOUTUBE CONSTANTS
'''
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
SPOTIFY_TOKEN: Final[str] = os.getenv("SPOTIFY_TOKEN")
SPOTIFY_SECRET: Final[str] = os.getenv("SPOTIFY_SECRET")
SPOTIFY_REDIRECT: str = 'http://localhost:3000/callback'
spotify_oauth = SpotifyOAuth(client_id=SPOTIFY_TOKEN, client_secret=SPOTIFY_SECRET, redirect_uri=SPOTIFY_REDIRECT)
sp = spotipy.Spotify(auth_manager=spotify_oauth)

@lru_cache(maxsize=20)
def get_spotify_song(search: str):
    track = sp.search(q=search, limit=1,type='track')
    artist = track['tracks']['items'][0]['artists'][0]['name']
    track_name = track['tracks']['items'][0]['name']
    return artist, track_name