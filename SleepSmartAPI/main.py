"""Main Flask API"""
from flask import Flask, jsonify
import xmltodict
import os
from dotenv import load_dotenv
import requests

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

APP = Flask(__name__)


@APP.route('/')
def hello_world():
    """Return string Hello, World!

    >>> hello_world()
    'Hello, World!'
    """

    return 'Hello, World!'

@APP.route('/plexapi')
def plex_api():
    """Access plex API playlists"""
    plex_api = os.getenv('PLEX_URL')
    response = requests.get(plex_api)
    content_dict = xmltodict.parse(response.content)
    return jsonify(content_dict)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
