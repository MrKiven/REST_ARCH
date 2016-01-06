# -*- coding: utf-8 -*-

import sys
import contextlib
import click


@contextlib.contextmanager
def _client_ctx(app_name, service, host, port):
    pass


@click.command()
@click.option('-h', '--host', default='localhost',
              help='service host(default localhost)')
@click.option('-p', '--port', default=None, help='service port')
@click.option('-r', '--rpc', default=False, is_flag=True,
              help='if use rpc connect')
@click.option('--profile', default=False, is_flag=True,
              help='Profile all apis calls')
def shell(host, port, rpc, profile):
    def embed_with_cli():
        import IPython
        del sys.exitfunc
        IPython.embed()
    embed_with_cli()
