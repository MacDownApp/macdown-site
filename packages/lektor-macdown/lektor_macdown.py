import base64
import functools
import json
import os
import re

import jinja2

from lektor.pluginsystem import Plugin
from six.moves import urllib


GITHUB_API_BASE_URL = 'https://api.github.com/'
STABLE_TAG_PATTERN = re.compile(r'^v[\d\.]+$')
CACHE_DIR = os.path.join(os.path.dirname(__file__), '_cache')


def get_endpoint(path, params=None):
    url = urllib.parse.urljoin(GITHUB_API_BASE_URL, path)
    if params is not None:
        url = url + '?' + '&'.join('{k}={v}'.format(
            k=key, v=params[key],
        ) for key in params)
    response = urllib.request.urlopen(url)
    return json.loads(response.read().decode('utf8'))


def get_latest_tag():
    tag_data_list = get_endpoint('/repos/MacDownApp/macdown/tags')
    tag = None
    for tag_data in tag_data_list:
        tag_name = tag_data['name']
        if STABLE_TAG_PATTERN.match(tag_name):
            tag = tag_name
            break
    assert tag is not None
    return tag


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


@cached('prism-components.json')
def get_prism_language_data():
    """Use the GitHub API to get Prism languages.
    """
    # Get Git URL of Prism submodule at the tag.
    data = get_endpoint(
        '/repos/MacDownApp/macdown/contents/Dependency/prism',
        params={'ref': get_latest_tag()},
    )
    components_str = download_endpoint(
        endpoint='/repos/PrismJS/prism/contents/components.js',
        ref=data['sha'],
    )
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
def get_language_aliase_data():
    """Get MacDown-maintained language aliases.
    """
    info_str = download_endpoint(
        endpoint=(
            '/repos/MacDownApp/macdown/contents/MacDown/Resources/'
            'syntax_highlighting.json'
        ),
        ref=get_latest_tag(),
    )
    return info_str


def get_language_notes():
    """Get custom notes for languages.

    The values are raw HTML content. A key can be either a Prism language ID,
    or a MacDown language alias.
    """
    path = os.path.join(os.path.dirname(__file__), 'language_notes.json')
    with open(path) as f:
        return json.load(f)


def get_language_infos():
    languages = json.loads(get_prism_language_data())['languages']
    del languages['meta']
    infos = {
        lang: ''
        for lang in languages
        if not lang.endswith('-extras')
    }

    aliases = json.loads(get_language_aliase_data())['aliases']
    infos.update({
        k: 'Alias to <code>{lang}</code>.'.format(lang=aliases[k])
        for k in aliases
    })

    notes = get_language_notes()
    for lang in notes:
        infos[lang] = notes[lang]

    infos = [(key, infos[key]) for key in sorted(infos.keys())]
    return infos


class MacDownPlugin(Plugin):

    name = 'MacDown'

    def on_setup_env(self, **extra):

        def render_syntax_table():
            t = self.env.jinja_env.get_template('macdown/syntaxtable.html')
            return jinja2.Markup(t.render(language_infos=language_infos))

        language_infos = get_language_infos()
        self.env.jinja_env.globals.update({
            'render_syntax_table': render_syntax_table,
        })
