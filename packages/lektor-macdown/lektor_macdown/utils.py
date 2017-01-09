import base64
import functools
import json
import os

from six.moves import urllib


GITHUB_API_BASE_URL = 'https://api.github.com/'
CACHE_DIR = os.path.join(os.path.dirname(__file__), '_cache')


def get_endpoint(path, params=None):
    url = urllib.parse.urljoin(GITHUB_API_BASE_URL, path)
    if params is not None:
        url = url + '?' + '&'.join('{k}={v}'.format(
            k=key, v=params[key],
        ) for key in params)
    response = urllib.request.urlopen(url)
    return json.loads(response.read().decode('utf8'))


def download_endpoint(endpoint, ref, encoding='utf-8'):
    data = get_endpoint(endpoint, params={'ref': ref})
    content_str = base64.b64decode(data['content']).decode(encoding)
    return content_str


def cached(filename):
    """Cache function results in file specified.
    """
    def _cached(func):

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if not os.path.exists(CACHE_DIR):
                os.makedirs(CACHE_DIR)
            cache_fs = os.path.join(CACHE_DIR, filename)
            if os.path.exists(cache_fs):
                with open(cache_fs) as f:
                    value = f.read()
            else:
                value = func(*args, **kwargs)
                with open(cache_fs, 'w') as f:
                    f.write(value)
            return value

        return wrapped

    return _cached
