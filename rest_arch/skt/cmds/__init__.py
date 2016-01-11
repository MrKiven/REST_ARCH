# -*- coding: utf-8 -*-

import logging
import click

from .serve import serve
from .shell import shell
from .bootstrap import bootstrap

logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def skt():
    pass

skt.add_command(serve)
skt.add_command(shell)
skt.add_command(bootstrap)
