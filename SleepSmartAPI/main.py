"""Main Flask API"""
import hashlib
import logging
import os
import urllib
from pprint import pprint

from flask import Flask, jsonify
import xmltodict
import requests

from dotenv import load_dotenv



def sha256(q_q):
    """Shortcut for getting hex digest of sha256 of string"""
    return hashlib.sha256(make_utf8(q_q)).hexdigest()

def make_utf8(q_q):
    """Make a string utf8 if it isn't"""
    if not isinstance(q_q, bytes):
        q_q = str(q_q).encode('utf-8')
    return q_q


logging.basicConfig(level=logging.DEBUG)

# refers to application_top
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')
DOTENV_PATH = os.path.join(APP_ROOT, '.env')
load_dotenv(DOTENV_PATH)

APP = Flask(__name__)

print(os.getenv('PLEX_URL'))



def change_path(url, new_path, add_query_params=None):
    """Change a url's path and add query params"""

    if add_query_params is None:
        add_query_params = []

    (scheme, netloc, _, query, fragment) = urllib.parse.urlsplit(url)
    q_q = urllib.parse.parse_qsl(query)
    newq = [(make_utf8(k), make_utf8(v)) for k, v in q_q if k.startswith('X-')]
    newq.extend(add_query_params)
    pprint((
        make_utf8(scheme),
        make_utf8(netloc),
        make_utf8(new_path),
        make_utf8(urllib.parse.urlencode(newq)),
        make_utf8(fragment),
    ))  # NOQA

    return urllib.parse.urlunsplit((
        make_utf8(scheme),
        make_utf8(netloc),
        make_utf8(new_path),
        make_utf8(urllib.parse.urlencode(newq)),
        make_utf8(fragment),
    ))  # NOQA


@APP.route('/')
def hello_world():
    """Return string Hello, World!

    >>> hello_world()
    'Hello, World!'
    """

    return 'Hello, World!'

#may need to clear the track dir?


@APP.route('/playlists')
def playlists():
    """Access plex API playlists"""
    playlists = os.getenv('PLEX_PLAYLISTS_URL')
    response = requests.get(playlists.format('playlists'))
    content_dict = xmltodict.parse(response.content)
    return jsonify(content_dict)

# @APP.route('/track_list')
# def tracklists():
#     """send list of track names, album/artist names,
#     etc to front end"""
#     items = os.getenv('PLEX_PLAYLIST_ITEMS')
#     response = requests.get(items.format('items'))
#     tracks = xmltodict.parse(response.content)
#     prefix = os.getenv('PLEX_TRACK_PREFIX')
#     suffix = os.getenv('PLEX_PARAMS')
#     for track in tracks['MediaContainer']['Track']:
#         response = requests.get(prefix + track['@title'] + suffix)
#         # print('/track_list' + track['@art'])
#
# @APP.route('/playlist_info')
# def items():
#     """access album art, song titles, and Album title"""
#     items = os.getenv('PLEX_PLAYLIST_ITEMS')
#     response = requests.get(items.format('items'))
#     tracks = xmltodict.parse(response.content)
#     prefix = os.getenv('PLEX_TRACK_PREFIX')
#     suffix = os.getenv('PLEX_PARAMS')
#     for track in tracks['MediaContainer']['Track']:
#         response = requests.get(prefix + track['@art'] + suffix)
#         print('tracks/' + track['@art'], 'wb')
#         # open.write(response.content)
#     return jsonify(tracks)

@APP.route('/tracks')
def items():
    """access items in playlists"""
    items_url = change_path(os.getenv('PLEX_URL'), "playlists/5238/items")
    response = requests.get(items_url)
    tracks = xmltodict.parse(response.content)
    for track in tracks['MediaContainer']['Track']:
        track_key = track['Media']['Part']['@key']
        response = requests.get(change_path(os.getenv('PLEX_URL'), track_key))
        pprint(track)
        with open(os.path.join("tracks", sha256(track_key)) + '.flac', 'wb') as f_f:
            f_f.write(response.content)
    return jsonify(tracks)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# @APP.route('/playlists/:p-id/items')
# def itemId():
#     """access each item/song in playlist"""
#     id = requests.get()
# flask route /playlists/:p-id/items
# /tracks/:id
