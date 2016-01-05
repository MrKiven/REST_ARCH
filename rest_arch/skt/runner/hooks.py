# -*- coding: utf-8 -*-

"""
Hooks around gunicorn runner.
"""

import os


def worker_term(worker):
    os.environ['SERVER_SHUTTINGDOWN'] = '1'


def post_worker_init(worker):
    os.environ.pop('SERVER_SHUTTINGDOWN', None)


def on_connected(worker, addr):
    from ...ctx import g
    if addr:
        g.set_conn_meta('client_addr', addr[0])


def post_fork(arbitor, worker):
    worker.app.chdir()
    from ..env import initialize
    initialize()


def when_ready(arbitor):
    pass
