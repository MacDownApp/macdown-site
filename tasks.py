from __future__ import unicode_literals

import datetime
import io
import json
import os

import invoke
import six

from lektor.builder import Builder
from lektor.cli import Context
from lektor.db import F
from lektor.project import Project
from lektor.reporter import CliReporter

if six.PY2:
    input = raw_input   # noqa


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
        yield '{}{}'.format(
            padright('/download/v{}/'.format(page['version']), 24),
            page['download_url'],
        )


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
    return '{}{}302'.format(
        padright('/download/latest/', 24),
        padright(latest['download_url'], 8),
    )


def generate_blog_post_redirects(pad):
    for post in pad.query('/blog'):
        redirect_url = post.url_path
        yield '{}{}'.format(
            padright('/blog/post/{}'.format(post['id']), 24),
            redirect_url,
        )
        yield '{}{}'.format(
            padright('/blog/post/{}/*'.format(post['id']), 24),
            redirect_url,
        )


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
        f.write('# Blog posts.')
        f.write('\n'.join(generate_blog_post_redirects(pad)))
        f.write('\n')

        f.write('\n')
        f.write('# Download redirects.')
        f.write('\n'.join(generate_download_redirects(pad)))
        f.write('\n')

        latest_redirect = get_latest_download_redirect(pad)
        if latest_redirect is not None:
            f.write('\n')
            f.write('# Latests version download linkt.')
            f.write(latest_redirect)
            f.write('\n')


blog_post_template = """id: {id}
---
title:
---
author: Tzu-ping Chung
---
pub_date: {today}
---
content:
"""


@invoke.task
def post(ctx, slug=None):
    project = Project.discover()
    env = project.make_env()
    pad = env.new_pad()

    blog = pad.get('/blog')
    latest_post = blog.children.first()
    if latest_post is None:
        next_id = 1
    else:
        next_id = latest_post['id'] + 1

    if slug is None:
        slug = input('Enter slug: ') or '__new_post__'

    new_dirname = os.path.join(
        ROOT_DIR, os.path.dirname(blog.source_filename), slug,
    )
    os.mkdir(new_dirname)

    contents_fn = os.path.join(new_dirname, 'contents.lr')
    with io.open(contents_fn, mode='w', encoding='utf8') as f:
        f.write(blog_post_template.format(
            id=next_id,
            today=datetime.date.today().strftime(r'%Y-%m-%d'),
        ))


release_template = """_model: release
---
channels:

stable
testing
---
build_number: {build_number}
---
version: {version}
---
dsa_signature: {dsa_signature}
---
length: {length}
---
min_sysver: {min_sysver}
---
download_url: {download_url}
---
pub_datetime: {pub_datetime}
---
note:

"""


@invoke.task
def release(ctx, path_to_info):
    project = Project.discover()
    env = project.make_env()
    pad = env.new_pad()

    later = datetime.datetime.now() + datetime.timedelta(hour=1)

    with io.open(path_to_info, encoding='utf8') as f:
        info = json.load(f)
    info.setdefault('min_sysver', '10.8')
    info.setdefault('pub_datetime', later.strftime(r'%Y-%m-%d %H:%M:%S'))
    info.setdefault(
        'download_url',
        'https://github.com/MacDownApp/macdown/releases/download/'
        'v{version}/MacDown.app.zip'.format(version=info['version']),
    )

    download = pad.get('/download')

    new_dirname = os.path.join(
        ROOT_DIR,
        os.path.dirname(download.source_filename),
        info['build_number'],
    )
    os.mkdir(new_dirname)

    contents_fn = os.path.join(new_dirname, 'contents.lr')
    with io.open(contents_fn, mode='w', encoding='utf8') as f:
        f.write(release_template.format(**info))
