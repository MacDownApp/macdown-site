from lektor.pluginsystem import Plugin


def volumize(value):
    try:
        value = float(value)
    except ValueError:
        value = 0
    if value == 0:
        return '0 bytes'
    elif value == 1:
        return '1 byte'
    for unit in ('bytes', 'KB', 'MB', 'GB',):
        if -1024 < value < 1024:
            return '{value:3.1f} {unit}'.format(value=value, unit=unit)
        value /= 1024
    return '{value:3.1f} {unit}'.format(value=value, unit='TB')


def nomalize_float(value):
    return str(value).rstrip('0').rstrip('.')


class HumanizePlugin(Plugin):

    name = 'Humanize'

    def on_setup_env(self, **extra):
        self.env.jinja_env.filters.update({
            'nomalize_float': nomalize_float,
            'volumize': volumize,
        })
