# -*- coding: utf-8 -*-
"""
rest_arch.async
~~~~~~~~~~~~~~~
# TODO
Define async tasks for all apis.
"""

import functools
import celery
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import gevent
from .conf import settings
if not settings.ASYNC_ENABLED:
    raise RuntimeError(
        'async function disabled, search for ASYNC_ENABLED setting'
    )
from .skt.env import is_in_container, initialize
from .skt.config import load_app_config
from .mock_queue import tasks as queue_tasks


def init_celery_app():
    if is_in_container():
        app_config = load_app_config()
        if not settings._loaded:
            initialize()
        if not settings.USE_MEMORY_MQ:
            if 'async_workers' in app_config.config:
                for q in app_config.config['async_workers']:
                    settings.celeryconfig.CELERY_QUEUES[q['name']] = {
                        "exchange": "SKT",
                        "routing_key": "api.%s" % q['name'],
                    }
            queues = {}
            queues.update(settings.celeryconfig.CELERY_QUEUES)
            settings.celeryconfig.CELERY_QUEUES = queues
    app = celery.Celery()
    app.config_from_object(settings.celeryconfig)
    return app

app = init_celery_app()


def send_task(service_slug, api, *args, **kwargs):
    if settings.USE_MEMORY_MQ:
        queue_tasks.put_nowait((service_slug, api, args, kwargs))
        return
    r = async_api.si(service_slug, api, *args, **kwargs). \
        apply_async(**kwargs)
    if service_slug != "dms":
        logger.info('{}.{}{} {}'.format(service_slug, api, args, r))
    return r


@app.task(max_retries=settings.TASK_MAX_RETRY_COUNT, bind=True)
def async_api(self, service_slug, api_name, *args, **kwargs):
    if service_slug in ('ess', 'tds'):
        return
    if service_slug == 'biz.member' and \
            api_name in ('signal_post_make_order',
                         'signal_post_process_order',
                         'signal_post_process_refund'):
        return

    client = find_client(service_slug, api_name)

    def retry_exc(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            except client.error as e:
                max_retries = kwargs.get('max_retries',
                                         settings.TASK_TE_MAX_RETRY_COUNT)
                retry_wait = kwargs.get('retry_wait',
                                        settings.TASK_THRIFT_ERROR_RETRY_WAIT)

                self.retry(exc=e, countdown=retry_wait,
                           max_retries=max_retries)
            except BaseException as e:
                max_retries = kwargs.get('max_retries',
                                         settings.TASK_UE_MAX_RETRY_COUNT)
                retry_wait = kwargs.get('retry_wait',
                                        settings.TASK_UNKOWN_ERROR_RETRY_WAIT)

                self.retry(exc=e, countdown=retry_wait,
                           max_retries=max_retries)

        return wrapper

    retry_exc(run_api)(client, self.request.id, api_name, *args)


def run_api(client, request_id, api_name, *args):
    service_slug = client.__name__

    logger.info("[{}] {}.{}{}".format(request_id,
                                      service_slug, api_name, args))

    with gevent.Timeout(10):
        if is_in_container():
            call = getattr(client, api_name)
            return call(*args)
        else:
            with client(timeout=10, fake=settings.FAKE_CLIENT) as c:
                call = getattr(c, api_name)
                return call(*args)


class AsyncRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task == "rest_arch.async.async_api":
            queue = args[0]
            if kwargs and kwargs.get('queue', '').startswith(args[0]):
                queue = kwargs.get('queue')
            return {
                'queue': queue,
            }
