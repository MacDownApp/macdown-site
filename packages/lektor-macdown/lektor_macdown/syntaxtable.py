import json
import os

from .utils import get_language_alias_data, get_prism_language_data


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

    aliases = json.loads(get_language_alias_data())['aliases']
    infos.update({
        k: 'Alias to <code>{lang}</code>.'.format(lang=aliases[k])
        for k in aliases
    })

    notes = get_language_notes()
    for lang in notes:
        infos[lang] = notes[lang]

    infos = [(key, infos[key]) for key in sorted(infos.keys())]
    return infos
