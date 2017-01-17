from __future__ import unicode_literals

import io
import json
import os
import sys

import six

from lektor.types import Type
from markupsafe import Markup

from .js import JavaScriptRunner
from .utils import (
    cached, download_endpoint, download_file, download_prism_script_files,
    get_prism_language_data, get_language_alias_data,
)


DISTRIB_EP = '/repos/jonschlinkert/remarkable/contents/dist/remarkable.min.js'


def get_prism_dependency_map():
    languages = json.loads(get_prism_language_data())['languages']
    languages.pop('meta')

    dependency_map = {}
    for key, value in six.iteritems(languages):
        requires = value.get('require', ())
        if not isinstance(requires, (tuple, list)):
            requires = [requires]
        dependency_map[key] = requires
    return dependency_map


def resolve_prism_components(language_set, dependency_map):
    """Resolve language dependency of a list of Prism components.

    Dependencies are added as needed, and the items reordered to
    produce a workable loading list.
    """
    resolved_list = []

    def put_lang(lang):
        try:
            resolved_list.remove(lang)
        except ValueError:  # Not found.
            pass
        resolved_list.append(lang)

    def dependency_gen(lang):
        try:
            deps = dependency_map[lang]
        except KeyError:
            return
        yield lang
        for dep in deps:
            yield dep
            for dep_dep in dependency_gen(dep):
                yield dep_dep

    for lang in language_set:
        for dep in dependency_gen(lang):
            put_lang(dep)

    resolved_list.append('core')
    return reversed(resolved_list)


def get_prism_script():
    container_dir = os.path.join(download_prism_script_files(), 'components')

    def read(name):
        with io.open(os.path.join(container_dir, name), encoding='utf8') as f:
            return f.read()

    content_map = {
        name[6:-7]: read(name)
        for name in os.listdir(container_dir)
        if name.endswith('.min.js')
    }
    dependency_map = get_prism_dependency_map()
    load_order = resolve_prism_components(content_map.keys(), dependency_map)
    prism_script = '\n'.join(content_map[name] for name in load_order)
    return prism_script


@cached('remarkable.min.js')
def get_remarkable_script():
    # TODO: Match this with MacDown's version.
    remarkable_script = download_endpoint(endpoint=DISTRIB_EP, ref='master')
    return remarkable_script


@cached('katex.min.js')
def get_katex_script():
    # TODO: Match this with MacDown's version.
    katex_script = download_file(
        'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js',
        encoding='utf-8',
    )
    return katex_script


class Renderer(object):
    """Wrapper for a Remarkable object do perform Markdown rendering.
    """
    def __init__(self):
        self.runner = JavaScriptRunner()

        # Setup syntax highlighting.
        aliases = json.loads(get_language_alias_data())['aliases']
        self.runner['aliases'] = aliases
        self.runner.evaluate(get_prism_script())

        # Setup math rendering.
        self.runner.evaluate(get_katex_script())

        # Setup Remarkable.
        self.runner.evaluate(get_remarkable_script())
        ext_dir = os.path.join(
            os.path.dirname(__file__),
            '_data',
            'remarkable-ext',
        )
        self.runner.evaluate("""
            var rmkb = new Remarkable('full', {
                html: true,
                highlight: function (str, lang) {
                    lang = aliases[lang] || lang;
                    var grammar = Prism.languages[lang];
                    // Empty string means input is unchanged.
                    return grammar ? Prism.highlight(str, grammar, lang) : '';
                }
            });
            rmkb.block.ruler.enable([ 'footnote' ]);
            rmkb.inline.ruler.enable([
                'footnote_inline',
                'ins', 'mark',
                'sub', 'sup'
            ]);
        """)
        for name in os.listdir(ext_dir):
            if not name.endswith('.js'):
                continue
            with io.open(os.path.join(ext_dir, name), encoding='utf8') as f:
                self.runner.evaluate(f)

    def render(self, md):
        self.runner['md'] = md
        result = self.runner.evaluate('rmkb.render(md);')
        return result


class Markdown(object):
    """Representation of a Markdown object.
    """
    renderer = Renderer()

    def __init__(self, source):
        self.source = source

    def __bool__(self):
        return bool(self.source)

    def __getattr__(self, key):
        if key == '_html':
            html = self.renderer.render(self.source)
            self._html = html
            return html
        return super(Markdown, self).__getattr__(key)

    def __str__(self):
        return self.html

    # Python 2 compatibility.
    if six.PY2:
        __nonzero__ = __bool__
        __unicode__ = __str__

        def __str__(self):
            return self.__unicode__().encode(sys.getdefaultencoding())

    def __html__(self):
        return Markup(self.html)

    @property
    def html(self):
        return self._html


class MarkdownDescriptor(object):
    """Describes the Markdown object to the type.
    """
    def __init__(self, source):
        self.source = source

    def __get__(self, obj, type=None):
        return Markdown(self.source)


class MarkdownType(Type):

    widget = 'multiline-text'

    def value_from_raw(self, raw):
        if raw.value is None:
            return raw.missing_value('Missing Markdown')
        return MarkdownDescriptor(raw.value or '')
