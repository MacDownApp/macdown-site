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


GITHUB_API_BASE_URL = 'https://api.github.com/'
STABLE_TAG_PATTERN = re.compile(r'^v[\d\.]+$')
CACHE_DIR = os.path.join(os.path.dirname(__file__), '_cache')

_cache_lock = threading.RLock()


class EndpointError(Exception):
    pass


def get_endpoint(path, params=None):
    url = urllib.parse.urljoin(GITHUB_API_BASE_URL, path)
    if params is not None:
        url = url + '?' + '&'.join('{k}={v}'.format(
            k=key, v=params[key],
        ) for key in params)
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        raise EndpointError(url)
    return json.loads(response.read().decode('utf8'))


def download_endpoint(endpoint, ref, encoding='utf-8'):
    data = get_endpoint(endpoint, params={'ref': ref})
    content_str = base64.b64decode(data['content']).decode(encoding)
    return content_str


def download_file(url, encoding=None):
    response = urllib.request.urlopen(url)
    data = response.read()
    if encoding:
        return data.decode(encoding)
    return data


def download_from_cdnjs(path, encoding='utf-8'):
    return download_file(
        'https://cdnjs.cloudflare.com/ajax/libs/' + path,
        encoding=encoding,
    )


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
    tag_data_list = get_endpoint('/repos/MacDownApp/macdown/tags')
    tag = None
    for tag_data in tag_data_list:
        tag_name = tag_data['name']
        if STABLE_TAG_PATTERN.match(tag_name):
            tag = tag_name
            break
    assert tag is not None
    return tag


@cached('prism-ref.txt')
def get_prism_ref():
    data = get_endpoint(
        '/repos/MacDownApp/macdown/contents/Dependency/prism',
        params={'ref': get_latest_stable_macdown_tag()},
    )
    return data['sha']


def download_prism_script_files():
    ref = get_prism_ref()
    container_dir = os.path.join(CACHE_DIR, 'prism-{}'.format(ref))
    if os.path.isdir(container_dir):
        return container_dir
    data = download_file(
        'https://github.com/PrismJS/prism/archive/{}.zip'.format(ref),
    )
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
    info_str = download_endpoint(
        endpoint=(
            '/repos/MacDownApp/macdown/contents/MacDown/Resources/'
            'syntax_highlighting.json'
        ),
        ref=get_latest_stable_macdown_tag(),
    )
    return info_str
