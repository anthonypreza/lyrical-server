import os

import requests
from bs4 import BeautifulSoup

GENIUS_BASE_URL = 'https://api.genius.com'
GENIUS_ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')
AUTH_HEADERS = {'Authorization': 'Bearer ' + GENIUS_ACCESS_TOKEN}


def get_song_info(name, artists):
    q = name.lower()
    if '(' in q:
        q = q.split('(')[0]
    for artist in artists:
        q += ' ' + str(artist['name']).lower()
    artist = artists[0]
    search_url = GENIUS_BASE_URL + '/search'
    data = {'q': q}
    response = requests.get(search_url, params=data, headers=AUTH_HEADERS)
    r = response.json()
    for hit in r['response']['hits']:
        if artist['name'].lower(
        ) in hit['result']['primary_artist']['name'].lower():
            song_info = hit
            return song_info


def get_lyrics(hit):
    song_url = hit['result']['url']
    page = requests.get(song_url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics


def get_lyrics_free_tier(hit):
    song_api_path = hit['result']['api_path']
    song_url = GENIUS_BASE_URL + song_api_path
    response = requests.get(song_url, headers=AUTH_HEADERS)
    r = response.json()
    embed_content = r['response']['song']['embed_content']
    return embed_content
