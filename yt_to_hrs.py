import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse

def get_playlist_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/playlist':
            return parse_qs(parsed_url.query)['list'][0]
    return None

def get_playlist_duration(playlist_id):
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    script_tag = soup.find("script", string=re.compile("var ytInitialData"))
    if not script_tag:
        return None

    json_text = re.search(r'var ytInitialData = (.+?);</script>', str(script_tag)).group(1)
    data = json.loads(json_text)

    total_seconds = 0
    videos = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']

    for video in videos:
        if 'playlistVideoRenderer' not in video:
            continue
        duration_text = video['playlistVideoRenderer']['lengthText']['simpleText']
        total_seconds += parse_duration(duration_text)

    return total_seconds

def parse_duration(duration):
    parts = duration.split(':')
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    else:
        return int(parts[0])

def main():
    playlist_url = input("Enter the YouTube playlist URL: ")
    playlist_id = get_playlist_id(playlist_url)
    
    if playlist_id:
        total_seconds = get_playlist_duration(playlist_id)
        if total_seconds is not None:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            print(f"Total duration of the playlist: {hours} hours and {minutes} minutes")
        else:
            print("Unable to retrieve playlist information")
    else:
        print("Invalid YouTube playlist URL")

if __name__ == "__main__":
    main()