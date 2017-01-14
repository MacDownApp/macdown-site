"""
This module provides :class:`AppCast` that can be used to generate
Sparkle-compatible appcasts.
"""

from __future__ import unicode_literals

MONTHS = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
]
WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def format_pubdate(pub_date):
    return (
        '{w}, {d.day} {m} {d.year} '
        '{d.hour:02}:{d.minute:02}:{d.second:02} {d:%z}'.format(
            d=pub_date, m=MONTHS[pub_date.month - 1],
            w=WEEKDAYS[pub_date.weekday()],
        )
    )


class AppCast(object):
    """Helper class that creates Sparkle appcasts.

    This is largely based on :class:`werkzeug.contrib.atom.AtomFeed`.
    """
    def __init__(self, title, link):
        self.title = title
        self.link = link
        self.items = []

    def add(self, title, description, pub_date, url, **kwargs):
        """Add a new item to the feed.

        Keyword arguments can contain:

        * `enclosed`: Whether Sparkle should download the archive.
        * `build`: Build number.
        * `version`: Human-readable version string.
        * `length`: Length of the archive in bytes, as an `int`.
        * `dsasign`: DSA signature.
        * `minsysver`: Minimum system version requirement.

        `minsysver` and `enclosed` are optional. All other arguments are
        required when `enclosed` is set to `True` (the default), otherwise
        they are optional.
        """
        minsysver = kwargs.pop('minsysver', None)
        kwargs['url'] = url
        kwargs.setdefault('enclosed', True)
        item = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'url': kwargs,
        }
        if minsysver:
            item['minsysver'] = minsysver
        self.items.append(item)

    def generate(self):
        """Return a generator that yields pieces of XML.
        """
        yield '<?xml version="1.0" encoding="utf-8"?>\n'
        yield '<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.or' \
              'g/xml-namespaces/sparkle" xmlns:dc="http://purl.org/dc/elemen' \
              'ts/1.1/">\n'
        yield '  <channel>\n'
        yield '    <title>{}</title>\n'.format(self.title)
        yield '    <link>{}</link>\n'.format(self.link)
        yield '    <description>Most recent changes with links to updates.' \
              '</description>\n'
        yield '    <language>en</language>\n'

        for item in self.items:
            yield '    <item>\n'
            yield '      <title>{}</title>\n'.format(item['title'])
            yield '      <description><![CDATA[{}]]></description>\n'.format(
                # Escape ']]>' in content.
                item['description'].replace(']]>', ']]]]><![CDATA[>'),
            )
            yield '      <pubDate>{}</pubDate>\n'.format(
                format_pubdate(item['pub_date']),
            )
            if 'minsysver' in item:
                yield (
                    '      <sparkle:minimumSystemVersion>{}'
                    '</sparkle:minimumSystemVersion>\n'.format(
                        item['minsysver'],
                    )
                )
            url = item['url']
            if url['enclosed']:
                yield (
                    '      <enclosure\n'
                    '       url="{url}"\n'
                    '       sparkle:version="{build}"\n'
                    '       sparkle:shortVersionString="{version}"\n'
                    '       length="{length}"\n'
                    '       sparkle:dsaSignature="{dsasign}"\n'
                    '       type="application/octet-stream" />\n'.format(**url)
                )
            else:
                yield '      <url>{}</url>\n'.format(url['url'])
            yield '    </item>\n'

        yield '  </channel>\n'
        yield '</rss>\n'

    def to_string(self):
        return ''.join(self.generate())
