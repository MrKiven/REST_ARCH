# -*- coding: utf-8 -*-

import sys
import contextlib
import click
from ..consts import DEFAULT_APP_PORT
from ...client import Client

import __main__


@contextlib.contextmanager
def _client_ctx(app_name, service, host, port):
    pass


@click.command()
@click.option('-h', '--host', default='localhost',
              help='service host(default localhost)')
@click.option('-p', '--port', default=DEFAULT_APP_PORT, help='service port')
@click.option('-r', '--rpc', default=False, is_flag=True,
              help='if use rpc connect')
@click.option('--profile', default=False, is_flag=True,
              help='Profile all apis calls')
def shell(host, port, rpc, profile):
    """
    # run a client in ipython
    """
    user_ns = __main__.__dict__
    c = Client(host, port)

    def embed_with_cli(client):
        import IPython
        del sys.exitfunc
        user_ns.update(dict(c=client))
        IPython.embed(user_ns=user_ns)
    embed_with_cli(c)
