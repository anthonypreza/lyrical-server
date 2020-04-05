import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

# load environment
UTIL_DIR: str = os.path.dirname(__file__)
DOTENV_PATH: str = os.path.join(
    UTIL_DIR, '..', '..', '.env') if '.env' in os.listdir(
        f'{UTIL_DIR}/../..' if UTIL_DIR else None) else os.path.join(
            os.path.dirname(__file__), '..', '..', '.env.local')
load_dotenv(DOTENV_PATH)

GENIUS_BASE_URL: str = 'https://api.genius.com'
GENIUS_ACCESS_TOKEN: str = os.getenv('GENIUS_ACCESS_TOKEN', '')
AUTH_HEADERS: Dict[str, str] = {
    'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'
}


def get_song_info(name: str,
                  artists: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Query Genius search API for song information matching the passed song name
    and list of artists. Returns the first matched instance as a dict of song
    info. Returns None if a match is not found.
    """
    q: str = name.lower()
    if '(' in q:
        q = q.split('(')[0]

    for a in artists:
        q += ' ' + str(a['name']).lower()

    artist: Dict[str, Any] = artists[0]
    search_url: str = f'{GENIUS_BASE_URL}/search'
    data: Dict[str, str] = {'q': q}
    response: requests.Response = requests.get(search_url,
                                               params=data,
                                               headers=AUTH_HEADERS)
    r: Dict[str, Any] = response.json()
    if 'error' in r:
        print(f"[ERROR] {r['error']} | {r['error_description']}")
        return None
    for hit in r['response']['hits']:
        if artist['name'].lower(
        ) in hit['result']['primary_artist']['name'].lower():
            song_info: Dict[str, Any] = hit
            return song_info
    return None


def get_lyrics(hit: Dict[str, Any]) -> Optional[str]:
    """
    Parses Genius HTML page for the provided hit from the Genius API.
    Returns text which is found in the <div class="lyrics"> tag.
    Returns None if the lyrics page or div are not found.
    """
    try:
        song_url: str = hit['result']['url']
        page: requests.Response = requests.get(song_url)
        html: BeautifulSoup = BeautifulSoup(page.text, 'html.parser')
        lyrics: str = html.find('div', class_='lyrics').get_text()
        return lyrics
    except TypeError as e:
        print(e)
        return None


def get_lyrics_free_tier(hit: Dict[str, Any]) -> Optional[str]:
    """
    Called in place of "get_lyrics" for servers that block Genius web calls.
    Returns embedded information for the hit by calling the Genius REST API.
    This information does not contain the actual lyrics, but a link to the
    lyrics page. Returns None if the hit's API path is not found.
    """
    try:
        song_api_path: str = hit['result']['api_path']
        song_url: str = GENIUS_BASE_URL + song_api_path
        response: requests.Response = requests.get(song_url,
                                                   headers=AUTH_HEADERS)
        r: Dict[str, Any] = response.json()
        embed_content: str = r['response']['song']['embed_content']
        return embed_content
    except TypeError as e:
        print(e)
        return None
