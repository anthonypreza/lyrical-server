"""
lyrical-v0 server application.
"""

import os
import argparse
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence, Union

from dotenv import load_dotenv  # type: ignore

from flask import Flask, Response, jsonify, request
from flask_cors import CORS  # type: ignore

from .utils.genius import get_lyrics, get_lyrics_free_tier, get_song_info
from .utils.nlp import get_most_common, tokenized_lyrics


class App(Flask):
    """
    Main application class.
    """
    def __init__(self, name: str) -> None:
        super(App, self).__init__(name)


# set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)

# load environment
SERVER_DIR: str = os.path.dirname(__file__)
DOTENV_PATH: str = os.path.join(
    SERVER_DIR, '..', '.env') if '.env' in os.listdir(
        f'{SERVER_DIR}/..' if SERVER_DIR else None) else os.path.join(
            os.path.dirname(__file__), '..', '.env.local')
load_dotenv(DOTENV_PATH)

# instantiate application class and set configuration
APP: App = App(__name__)
APP.config.from_envvar('FLASK_CONFIG')
API_ROOT: str = '/api/v0'

# set up cross-origin resource sharing
cors: CORS = CORS(APP,
                  resources={r'/*': {
                      'origins': '*'
                  }},
                  supports_credentials=True)


@APP.route('/', methods=['GET'])
def root() -> Response:
    """
    Handle GET requests to root endpoint.
    """
    res: Response = Response('Web root for Lyrical API')
    return res


@APP.route(API_ROOT + '/get_lyrics', methods=['GET', 'POST'])
def lyrics() -> Response:
    """
    Handle POST requests with valid data and invalid GET requests
    to "get_lyrics" endpoint.
    Upon success, returns a Response containing the lyrics of the song
    that is queried.
    Returns a warning response if invalid GET request is issued.
    """
    if request.method == 'POST' and request.data:
        # extract request data and get song information
        data: Dict[str, Any] = json.loads(request.data)
        track_name: str = data['track_name']
        artists: List[Dict[str, Any]] = data['artists']
        song_info: Optional[Dict[str,
                                 Any]] = get_song_info(track_name, artists)

        # attempt to get lyrics for first returned hit
        if song_info:
            try:
                lyrics: Optional[str] = get_lyrics(song_info)
                res: Response = jsonify(lyrics)
            except Exception as e:
                print(e)
                lyrics = get_lyrics_free_tier(song_info)
                res = jsonify(lyrics)
            return res
        return jsonify(None)
    else:
        get_response: str = 'GET not supported. Did you mean to POST?'
        return Response(get_response)


@APP.route(API_ROOT + '/wordcloud', methods=['GET', 'POST'])
def wordcloud() -> Union[Response, str]:
    """
    Handle POST requests with valid data and invalid GET requests
    to "wordcloud" endpoint.
    Upon success, returns a JSON Response with the most common words
    in the user's top 50 Spotify tracks.
    Returns a warning response if invalid GET request is issued.
    """
    if request.method == 'POST' and request.data:
        # extract request data
        data: Dict[str, Any] = json.loads(request.data)
        # save data
        track_list: List[Dict[str, Any]] = data['top_tracks']
        # song_names = [t['name'] for t in track_list]
        # artist_names = [t['artists'] for t in track_list]

        # get lyrics
        hits: List[Optional[Dict[str, Any]]] = [
            get_song_info(t['name'], t['artists']) for t in track_list
        ]
        cleaned_hits: List[Dict[str, Any]] = [h for h in hits if h]
        lyrics: List[Optional[str]] = [get_lyrics(h) for h in cleaned_hits]

        # for saving data to train RNN
        # records = [{
        #     'song': t['name'],
        #     'artist_names': t['artists'],
        #     'hit': h,
        #     'lyrics': l
        # } for t, h, l in zip(track_list, hits, lyrics)]

        # df = pd.DataFrame.from_records(records)
        # df.to_csv('data/tracks.csv')

        # build list of lists of tokens
        token_list: List[List[str]] = [
            tokenized_lyrics(l) for l in lyrics if l
        ]
        # flatten the list of lists
        word_list: List[str] = [word for array in token_list for word in array]
        # get most common words
        most_common: List[Dict[str, Any]] = get_most_common(word_list)
        return jsonify(most_common)
    # handle invalid GET requests
    else:
        get_response: str = 'GET not supported. Did you mean to POST?'
        return get_response


@APP.errorhandler(401)
def page_not_found() -> Response:
    """
    Handle 401 errors.
    """
    res: Response = Response('Not found')
    return res


def parse_args(args: Sequence[str]) -> argparse.Namespace:
    """
    Parse arguments for direct script invocation.
    """
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='Development server')
    argparser.add_argument('-p',
                           '--port',
                           type=int,
                           default=8000,
                           help='Port for HTTP server (default=%d).' % 8000)
    argparser.add_argument('-d',
                           '--debug',
                           action='store_true',
                           default=False,
                           help='Debug mode.')
    return argparser.parse_args(args)


def main() -> None:
    """
    Run the development server.
    """
    logger: logging.Logger = logging.getLogger(__name__)
    args: argparse.Namespace = parse_args(sys.argv[1:])
    logger.info('Starting server on port %s with debug=%s', args.port,
                args.debug)
    secret_key: bytes = b'R0Rl1C0ByYZM9IX3t2EQ1FgigOAx9Wo4'
    APP.secret_key = secret_key
    APP.run(host='0.0.0.0', port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
