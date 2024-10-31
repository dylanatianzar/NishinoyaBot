import os
from dotenv import load_dotenv
from typing import Final
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from urllib import parse, request

'''
YOUTUBE CONSTANTS
'''
load_dotenv()
GOOGLE_KEY: Final[str] = os.getenv("GOOGLE_KEY")
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=GOOGLE_KEY)

def search_YT(search: str):
    searchResponse = youtube.search().list(
        part = 'snippet',
        maxResults = 5,
        q = search,
        regionCode = 'us',
        relevanceLanguage = 'en',
        type = 'video'
    ).execute()
    videoIds = []
    for entry in searchResponse['items']:
        videoIds.append(entry['id'].get('videoId'))
    return videoIds

def get_YT_title(url):
    html_content = request.urlopen(url).read().decode()
    title = re.search(r'<title>(.*?) - YouTube</title>', html_content)
    return title.group(1) if title else "Title not found"