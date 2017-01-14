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


class HumanizePlugin(Plugin):

    name = 'Humanize'

    def on_setup_env(self, **extra):
        self.env.jinja_env.filters.update({
            'volumize': volumize,
        })
