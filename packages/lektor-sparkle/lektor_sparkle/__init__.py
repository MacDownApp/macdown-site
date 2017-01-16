import re
import sys

import lektor.pluginsystem
import lektor.types
import six

from .buildprograms import AppCastBuildProgram, AppCastSource


class BuildNumberType(lektor.types.FloatType):

    trailing_fraction_pattern = re.compile(r'(\.[1-9]*)0+$')

    def value_from_raw(self, raw):
        value = str(super(BuildNumberType, self).value_from_raw(raw))
        value = self.trailing_fraction_pattern.sub(r'\1', value)
        return value.rstrip('.')


class SparklePlugin(lektor.pluginsystem.Plugin):

    name = 'Sparkle'
    description = 'Lektor Sparkle AppCast generator.'

    def get_config_value(self, cast_id, key):
        config = self.get_config()
        full_key = '{}.{}'.format(cast_id, key)

        if key.startswith('_'):
            return config['{}.{}'.format(cast_id, key)]

        tb = None
        while True:
            try:
                return config['{}.{}'.format(cast_id, key)]
            except KeyError:
                tb = tb or sys.exc_info()[2]
                try:
                    parent = config['{}.{}'.format(cast_id, 'inherits')]
                    assert parent in config.sections()
                except (AssertionError, KeyError):
                    six.reraise(KeyError, KeyError(full_key), tb)
                cast_id = parent
        raise KeyError(full_key)

    def is_appcast_enabled(self, cast_id):
        return self.get_config().get_bool('{}._enabled'.format(cast_id), True)

    def on_setup_env(self, **extra):
        self.env.add_build_program(AppCastSource, AppCastBuildProgram)
        self.env.types['build_number'] = BuildNumberType

        @self.env.virtualpathresolver('appcast')
        def appcast_path_resolver(node, pieces):
            if len(pieces) != 1:
                return
            cast_id = pieces[0]
            config = self.get_config()
            if cast_id not in config.sections():
                return
            if not self.is_appcast_enabled(cast_id):
                return

            source_path = self.get_config_value(cast_id, 'source_path')
            if node.path == source_path:
                return AppCastSource(node, cast_id, plugin=self)

        @self.env.generator
        def generate_appcasts(source):
            for cast_id in self.get_config().sections():
                if not self.is_appcast_enabled(cast_id):
                    continue
                source_path = self.get_config_value(cast_id, 'source_path')
                if source.path == source_path:
                    yield AppCastSource(source, cast_id, self)
