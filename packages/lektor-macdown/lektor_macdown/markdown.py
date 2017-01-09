from __future__ import unicode_literals

import sys

import six
import WebKit

from lektor.types import Type
from markupsafe import Markup

from .utils import cached, download_endpoint


DISTRIB_EP = '/repos/jonschlinkert/remarkable/contents/dist/remarkable.min.js'


@cached('remarkable.min.js')
def get_remarkable_script():
    # TODO: Match this with MacDown's version.
    remarkable_script = download_endpoint(endpoint=DISTRIB_EP, ref='master')
    return remarkable_script


class Renderer(object):
    """Wrapper for a Remarkable object do perform Markdown rendering.
    """
    def __init__(self):
        self.ctx = WebKit.JSContext.alloc().init()
        self.ctx.evaluateScript_(get_remarkable_script())
        self.ctx.evaluateScript_("""
            var rmkb = new Remarkable('full', { html: true });
            rmkb.block.ruler.enable([ 'footnote' ]);
            rmkb.inline.ruler.enable([
                'footnote_inline',
                'ins', 'mark',
                'sub', 'sup'
            ]);
        """)

    def render(self, md):
        self.ctx.setObject_forKeyedSubscript_(md, 'md')
        result = self.ctx.evaluateScript_('rmkb.render(md);')
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
