from __future__ import unicode_literals

import base64
import functools
import io
import json
import os
import re
import threading
import zipfile

from six.moves import urllib
import requests


GITHUB_API_BASE_URL = 'https://api.github.com/'
STABLE_TAG_PATTERN = re.compile(r'^v[\d\.]+$')
CACHE_DIR = os.path.join(os.path.dirname(__file__), '_cache')

_cache_lock = threading.RLock()


class EndpointError(Exception):
    pass


def __json_from_github(path, ref=None):
    """Get JSON data from MacDown repository on GitHub.
    """
    url = 'https://api.github.com/repos/MacDownApp/macdown' + path
    return requests.get(url, params={'ref': ref}).json()


def download_from_cdnjs(path, encoding='utf-8'):
    return requests.get('https://cdnjs.cloudflare.com/ajax/libs/' + path).text


def cached(filename):
    """Cache function results in file specified.
    """
    def _cached(func):

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            with _cache_lock:
                cache_fs = os.path.join(CACHE_DIR, filename)
                if os.path.exists(cache_fs):
                    with io.open(cache_fs, encoding='utf8') as f:
                        value = f.read()
                else:
                    value = func(*args, **kwargs)
                    if isinstance(value, bytes):
                        value = value.decode('utf8')
                    if not os.path.exists(CACHE_DIR):
                        os.makedirs(CACHE_DIR)
                    with io.open(cache_fs, mode='w', encoding='utf8') as f:
                        f.write(value)
            return value

        return wrapped

    return _cached


@cached('macdown-tag.txt')
def get_latest_stable_macdown_tag():
    tags = map(lambda data: data['name'], __json_from_github('/tags'))
    return next(x for x in tags if STABLE_TAG_PATTERN.match(x))


@cached('prism-ref.txt')
def get_prism_ref():
    return __json_from_github(
        '/contents/Dependency/prism',
        ref=get_latest_stable_macdown_tag())['sha']


def download_prism_script_files():
    ref = get_prism_ref()
    container_dir = os.path.join(CACHE_DIR, 'prism-{}'.format(ref))
    if os.path.isdir(container_dir):
        return container_dir
    url = 'https://github.com/PrismJS/prism/archive/{}.zip'.format(ref)
    data = requests.get(url).content
    with zipfile.ZipFile(io.BytesIO(data)) as zipf:
        zipf.extractall(path=CACHE_DIR)
    return container_dir


@cached('prism-components.json')
def get_prism_language_data():
    container_dir = download_prism_script_files()
    with open(os.path.join(container_dir, 'components.js')) as f:
        components_str = f.read()

    # Make this string JSON-compatible.
    components_str = components_str[
        components_str.find('{'):components_str.rfind('}') + 1
    ]
    components_str_lines = [
        line for line in components_str.splitlines(True)
        if not line.strip().startswith('//')
    ]
    return ''.join(components_str_lines)


@cached('macdown-aliases.json')
def get_language_alias_data():
    """Get MacDown-maintained language aliases.
    """
    path = '/contents/MacDown/Resources/syntax_highlighting.json'
    data = __json_from_github(path, ref=get_latest_stable_macdown_tag())
    return base64.b64decode(data['content']).decode('utf-8')
