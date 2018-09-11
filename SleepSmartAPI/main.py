"""Main Flask API"""
import urllib
import os
import logging
from dotenv import load_dotenv

from flask import Flask, jsonify
import xmltodict
import requests

logging.basicConfig(level=logging.DEBUG)

# refers to application_top
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

APP = Flask(__name__)

print(os.getenv('PLEX_URL'))


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

@APP.route('/track_list')
def tracklists():
    """send list of track names, album/artist names,
    etc to front end"""
    items = os.getenv('PLEX_PLAYLIST_ITEMS')
    response = requests.get(items.format('items'))
    tracks = xmltodict.parse(response.content)
    prefix = os.getenv('PLEX_TRACK_PREFIX')
    suffix = os.getenv('PLEX_PARAMS')
    for track in tracks['MediaContainer']['Track']:
        response = requests.get(prefix + track['@art'] + suffix)
        print('/track_list' + track['@art'])


@APP.route('/tracks')
def items():
    """access items in playlists"""
    items = os.getenv('PLEX_PLAYLIST_ITEMS')
    response = requests.get(items.format('items'))
    tracks = xmltodict.parse(response.content)
    prefix = os.getenv('PLEX_TRACK_PREFIX')
    suffix = os.getenv('PLEX_PARAMS')
    for track in tracks['MediaContainer']['Track']:
        response = requests.get(prefix + track['Media']['Part']['@key'] + suffix)
        print('tracks/' + track['Media']['@id'] + '.flac', 'wb')
        .write(response.content)
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
