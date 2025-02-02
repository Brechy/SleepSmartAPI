"""Main Flask API"""
import hashlib
import os
import urllib
from pprint import pprint

from flask import jsonify, send_from_directory
import flask
import requests
import xmltodict
from dotenv import load_dotenv

from flask_cors import CORS

# refers to application_top
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')
DOTENV_PATH = os.path.join(APP_ROOT, '.env')
load_dotenv(DOTENV_PATH)

APP = flask.Flask(__name__, static_folder='tracks')
CORS(APP)

pprint(os.getenv('PLEX_URL'))

STOPPED_STATUS = 'STOPPED_STATUS'
PLAYING_STATUS = 'PLAYING_STATUS'
bear_status = STOPPED_STATUS


def sha256(q_q):
    """Shortcut for getting hex digest of sha256 of string"""
    return hashlib.sha256(make_utf8(q_q)).hexdigest()


def make_utf8(q_q):
    """Make a string utf8 if it isn't"""
    if not isinstance(q_q, bytes):
        q_q = str(q_q).encode('utf-8')
    return q_q


def change_path(url, new_path, add_query_params=None):
    """Change a url's path and add query params/custom headers"""

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

    return 'Welcome to SleepSmart! Get some rest.'


@APP.route('/status', methods=['GET', 'POST'])
def status():
    """return status of ON to Bear with AUDIO attached"""

    global bear_status

    if flask.request.method == 'GET':
        payload = {
            'resp': 'Play that funky music!',
            'status': bear_status,
            'track_id': [
                sha256('/library/parts/5190/1518806852/file.opus') + '.opus',
                sha256('/library/parts/5192/1496247087/file.opus') + '.opus',
                sha256('/library/parts/5194/1537019238/file.opus') + '.opus',
                sha256('/library/parts/5193/1457284625/file.opus') + '.opus',
                sha256('/library/parts/5191/1525458211/file.opus') + '.opus'

            ]}
        return jsonify(payload)

    if flask.request.method == 'POST':
        if flask.request.json['status'] == 'PLAY':
            bear_status = PLAYING_STATUS
        else:
            bear_status = STOPPED_STATUS
        return '=^.^='

@APP.route('/tracks/<track_id>')
def send_audio(track_id):
    """sending file from tracks dir"""
    pprint(track_id)
    pprint(os.getenv('TRACKS_FOLDER'))
    return send_from_directory(os.getenv('TRACKS_FOLDER'),
                               track_id)


@APP.route('/playlists')
def playlists():
    """Access plex API playlists"""
    playlists = os.getenv('PLEX_PLAYLISTS_URL')
    response = requests.get(playlists.format('playlists'))
    content_dict = xmltodict.parse(response.content)
    return jsonify(content_dict)


@APP.route('/tracks')
def items():
    """access items in playlists"""
    items_url = change_path(
        os.getenv('PLEX_PLAYLIST_ITEMS'), "playlists/5353/items")
    response = requests.get(items_url)
    tracks = xmltodict.parse(response.content)
    for track in tracks['MediaContainer']['Track']:
        track_key = track['Media']['Part']['@key']
        response = requests.get(change_path(os.getenv('PLEX_URL'), track_key))
        pprint(track)
        with open(os.path.join("tracks", sha256(track_key)) + '.ogg', 'wb') as f_f:
            f_f.write(response.content)
    return jsonify(tracks)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
