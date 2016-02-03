# -*- coding: utf-8 -*-
import logging

import functools
import threading
import gevent
from gevent.queue import Queue
from .client import clients
from .conf import settings
from .ves.env import is_in_container, is_in_dev

logger = logging.getLogger(__name__)


class Task(object):
    def __init__(self, service, api, args, kwargs):
        self.service = service
        self.api = api
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def create(cls, service, api, args, kwargs):
        if service is None:
            logger.info('create signal: {}{}'.format(api, args))
            return SignalTask(None, api, args, kwargs)
        logger.info('create async task: {}.{}{}'.format(service, api, args))
        return SimpleTask(service, api, args, kwargs)

    def call_api(self, service):
        from .async import find_client

        client = find_client(service, self.api)
        countdown = self.kwargs.get('countdown')
        if countdown:
            gevent.sleep(countdown)

        if is_in_container():
            _client_ctx = client.connection_ctx
        else:
            _client_ctx = functools.partial(client, fake=is_in_dev())

        with _client_ctx() as c:
            logger.info('calling async api: {}.{}{}'.format(
                service, self.api, self.args))
            call = getattr(c, self.api)
            call(*self.args)


class SimpleTask(Task):
    def execute(self):
        if self.service == 'ees':
            return
        self.call_api(self.service)


class SignalTask(Task):
    def execute(self):
        signal = self.api

        _get_slug = lambda x: x.split('.')[1]

        for i in clients:
            if signal in clients[i].apis:
                self.call_api(_get_slug(i))


def worker():
    while True:
        service, api, args, kwargs = tasks.get()
        task = Task.create(service, api, args, kwargs)
        t = threading.Thread(target=task.execute, args=())
        t.setDaemon(True)
        t.start()

if settings.USE_MEMORY_MQ:
    tasks = Queue()
    worker_thread = threading.Thread(target=worker, args=())
    worker_thread.setDaemon(True)
    worker_thread.start()
