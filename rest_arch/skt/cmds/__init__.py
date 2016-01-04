# -*- coding: utf-8 -*-

import logging
import click


logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def skt():
    pass

skt.add_command()
