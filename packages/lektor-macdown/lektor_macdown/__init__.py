import jinja2
import lektor.pluginsystem

from .markdown import MarkdownType
from .syntaxtable import get_language_infos


class MacDownPlugin(lektor.pluginsystem.Plugin):

    name = 'MacDown'
    description = 'Utilities for the MacDown site.'

    def on_setup_env(self, **extra):
        language_infos = get_language_infos()

        def render_syntax_table():
            t = self.env.jinja_env.get_template('macdown/syntaxtable.html')
            return jinja2.Markup(t.render(language_infos=language_infos))

        self.env.types['remarkable_markdown'] = MarkdownType
        self.env.jinja_env.globals.update({
            'render_syntax_table': render_syntax_table,
        })
