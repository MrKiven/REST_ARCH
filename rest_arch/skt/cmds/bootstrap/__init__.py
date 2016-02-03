# -*- coding: utf-8 -*-

import sys
import os
import logging
import contextlib
import click
import subprocess
from jinja2 import Environment, FileSystemLoader


logger = logging.getLogger(__name__)
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'helloworld')

cwd = os.getcwd()


@contextlib.contextmanager
def cd(dir):
    os.chdir(dir)
    yield dir
    os.chdir(cwd)


def mkdir_p(name, strict=False):
    if os.path.exists(name) and os.path.isdir(name):
        return
    try:
        os.mkdir(name)
    except OSError:
        logger.warning("cannot mkdir %s", name)
        if strict:
            sys.exit(1)

jinja_env = Environment(loader=FileSystemLoader(template_dir))


def render_template(template, filename=None, folder='.', mapping=None):
    """Render ``template`` to ``filename`` with ``mapping``.
    :param template: template file name, e.g. 'settings.py.jinja'
    :param filename: filename to store as, e.g. 'settings.py'
    :param folder: target file folder, e.g. '.'
    :param mapping: key value mappings to render with
    """
    if mapping is None:
        mapping = {}

    if filename is None:
        if not template.endswith('.jinja'):
            raise ValueError("Filename extension '.jinja' required")
        filename = template[:-len('.jinja')]

    path = os.path.join(folder, filename)
    content = jinja_env.get_template(template).render(**mapping)

    if os.path.exists(path):
        logger.warn("%s already exists, skipping...", os.path.normpath(path))
        return

    mkdir_p(folder)

    logger.info("Rendering %s...", os.path.normpath(path))

    with open(path, 'w') as f:
        f.write(content.encode('utf8'))

    return path


def validate_app_id(ctx, argument, value):
    if len(value.split('.')) != 2:
        raise click.BadParameter("AppId should be like 'team.proj', "
                                 "with 2 elements")

    if not all(map(unicode.islower, value.split('.'))):
        raise click.BadParameter("AppId should be like 'team.proj', all "
                                 "in lower case")
    return value


def validate_service_name(ctx, argument, value):
    if not value:
        raise click.BadParameter("Service name should not be empty")

    if not value.isalpha():
        raise click.BadParameter("Service name should be all letters[A-Za-z]")

    if not value[0].isupper():
        raise click.BadParameter("Service name should start with [A-Z]")
    return value


@click.command()
@click.option('--app-id', prompt="Applicattion id (e.g. arch.note)",
              callback=validate_app_id, help="App ID like 'team.proj'")
@click.option('--service-name', prompt="Service name (pascal style)",
              callback=validate_service_name,
              help="Service name like 'Note'")
def bootstrap(app_id, service_name):
    """
    # generate a demo app
    """
    from rest_arch import __version__
    app_slug = package_name = app_id.split('.')[1]
    mapping = dict(app_id=app_id,
                   service=service_name,
                   package=package_name,
                   app_slug=app_slug,
                   arch_version=__version__)
    logger.info("Createing new project: %s", app_id)

    mkdir_p(app_id)

    with cd(app_id):
        render_template('app.py.jinja', mapping=mapping,
                        folder=package_name)
        render_template('models.py.jinja', mapping=mapping,
                        folder=package_name)
        render_template('settings.py.jinja', mapping=mapping,
                        folder=package_name)
        render_template('celeryconfig.py.jinja', mapping=mapping,
                        folder=package_name)
        render_template('requirements.txt.jinja', mapping=mapping)
        render_template('app.yaml.jinja', mapping=mapping)
        render_template('__init__.py.jinja', mapping=mapping,
                        folder=package_name)

        subprocess.check_call(['git', 'init'])
        logger.info("Bootstrap completed.")
        logger.info("Run `skt serve` in %s/ "
                    "to start server.", app_id)


if __name__ == '__main__':
    # pylint: disable=E1120
    bootstrap()
