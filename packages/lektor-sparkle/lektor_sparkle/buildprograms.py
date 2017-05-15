import click
import markupsafe
import pytz
import six

from lektor.build_programs import BuildProgram
from lektor.context import get_ctx, url_to
from lektor.db import F
from lektor.environment import Expression
from lektor.sourceobj import VirtualSourceObject
from lektor.utils import build_url

from .appcasts import AppCast


class AppCastSource(VirtualSourceObject):
    """Source object for an appcast.
    """
    def __init__(self, parent, cast_id, plugin):
        super(AppCastSource, self).__init__(parent)
        self.plugin = plugin
        self.cast_id = cast_id

    def __getattr__(self, item):
        try:
            return self.plugin.get_config_value(self.cast_id, item)
        except KeyError:
            raise AttributeError(item)

    @property
    def cast_name(self):
        return self.plugin.get_config_value(self.cast_id, 'name')

    @property
    def path(self):
        return '{}@appcast/{}'.format(self.parent.path, self.cast_id)

    @property
    def url_path(self):
        p = self.plugin.get_atom_config(self.feed_id, 'url_path')
        return p or build_url([self.parent.url_path, self.filename])


class AppCastBuildProgram(BuildProgram):
    """Program to build the appcast.
    """
    def produce_artifacts(self):
        self.declare_artifact(
            self.source.url_path,
            sources=list(self.source.iter_source_filenames()),
        )

    def build_artifact(self, artifact):
        ctx = get_ctx()
        source = self.source

        appcast = AppCast(
            title=source.cast_name,
            link=url_to(source, external=True),
        )

        try:
            expr = Expression(ctx.env, source.items)
        except AttributeError:
            items = source.parent.children
        else:
            items = expr.evaluate(ctx.pad)

        if source.item_model:
            items = items.filter(F._model == source.item_model)
        items = items.order_by('-build_number')

        for item in items:
            with ctx.changed_base_url(item.url_path):
                description = six.text_type(markupsafe.escape(item['note']))

            try:
                offset = int(source.timezone)
            except ValueError:
                tzinfo = pytz.timezone(source.timezone)
            else:
                tzinfo = pytz.FixedOffset(offset)
            pub_date = item['pub_datetime'].replace(tzinfo=tzinfo)

            try:
                build_number = str(item['build_number'])
                if '.' in build_number:
                    build_number = build_number.rstrip('0').rstrip('.')
                appcast.add(
                    title='Version {}'.format(item['version']),
                    description=description,
                    pub_date=pub_date,
                    url=item['download_url'],
                    build=build_number,
                    version=item['version'],
                    length=item['length'],
                    dsasign=item['dsa_signature'],
                    minsysver=item['min_sysver'],
                )
            except Exception as e:
                msg = '{}: {}'.format(item.id, e)
                click.echo(click.style('E', fg='red') + ' ' + msg)

        with artifact.open('wb') as f:
            f.write(appcast.to_string().encode('utf-8'))
