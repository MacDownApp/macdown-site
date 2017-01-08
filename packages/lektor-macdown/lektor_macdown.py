from lektor.pluginsystem import Plugin


def render_syntax_table():
    pass


class MacDownPlugin(Plugin):

    name = 'MacDown'

    def on_setup_env(self, **extra):
        self.env.jinja_env.globals.update({
            'render_syntax_table': render_syntax_table,
        })
