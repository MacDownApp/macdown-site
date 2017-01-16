from __future__ import unicode_literals

import io
import os

import invoke

from lektor.builder import Builder
from lektor.cli import Context
from lektor.db import F
from lektor.reporter import CliReporter


ROOT_DIR = os.path.dirname(__file__)


def padright(s, unit):
    pad = ' ' * (unit - len(s) % unit)
    return '{}{}'.format(s, pad)


def get_static_redirect():
    redirects_fn = os.path.join(ROOT_DIR, 'redirects.txt')
    with io.open(redirects_fn, encoding='utf8') as f:
        return f.read()


def generate_download_redirects(pad):
    for page in pad.query('/download'):
        from_url = '/download/v{}/'.format(page['version'])
        try:
            redirect_url = page['download_url']
        except KeyError:
            continue
        yield '{}{}'.format(padright(from_url, 24), redirect_url)


def get_latest_download_redirect(pad):
    latest = (
        pad
        .query('/download')
        .filter(F.channels.contains('stable'))
        .order_by('-build_number')
        .first()
    )
    if not latest:
        return None
    from_url = '/download/latest/'
    try:
        redirect_url = latest['download_url']
    except KeyError:
        return None
    return '{}{}302'.format(padright(from_url, 24), padright(redirect_url, 8))


@invoke.task
def build(ctx):
    lektor_cli_ctx = Context()
    lektor_cli_ctx.load_plugins()

    env = lektor_cli_ctx.get_env()
    pad = env.new_pad()
    output_to = 'build'

    # This is essentially `lektor build --output-path build`.
    with CliReporter(env, verbosity=0):
        builder = Builder(pad, output_to)
        builder.build_all()

    # Generate redirect file.
    redirect_filename = os.path.join(ROOT_DIR, output_to, '_redirects')
    with io.open(redirect_filename, mode='w', encoding='utf8') as f:
        static_redirect = get_static_redirect()
        f.write(static_redirect)
        if not static_redirect.endswith('\n'):
            f.write('\n')
        f.write('\n')
        f.write('\n'.join(generate_download_redirects(pad)))
        f.write('\n')

        latest_redirect = get_latest_download_redirect(pad)
        if latest_redirect is not None:
            f.write('\n')
            f.write(latest_redirect)
            f.write('\n')
