import json
import os
import re

from .utils import cached, download_endpoint, get_endpoint


STABLE_TAG_PATTERN = re.compile(r'^v[\d\.]+$')


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


@cached('prism-components.json')
def get_prism_language_data():
    """Use the GitHub API to get Prism languages.
    """
    # Get Git URL of Prism submodule at the tag.
    data = get_endpoint(
        '/repos/MacDownApp/macdown/contents/Dependency/prism',
        params={'ref': get_latest_stable_macdown_tag()},
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
        ref=get_latest_stable_macdown_tag(),
    )
    return info_str


def get_language_notes():
    """Get custom notes for languages.

    The values are raw HTML content. A key can be either a Prism language ID,
    or a MacDown language alias.
    """
    path = os.path.join(
        os.path.dirname(__file__),
        '_data',
        'language_notes.json',
    )
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
