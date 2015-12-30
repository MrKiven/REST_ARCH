# -*- coding: utf-8 -*-

import functools
import logging
import os


class Service(dict):

    def __setattr__(self, name, value):
        return super(Service, self).__setitem__(name, value)

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)

    def dispather(self, cls):
        def _decorate(func):
            @functools.wraps(func)
            def wrapper(cls_self, *args):
                return self.run(cls_self, func, args, logger)
            return wrapper

        logger = logging.getLogger(cls.__module__)

    def get_dispatcher_class(self):
        if self.thrift_service_dispatcher_cls is None:
            raise RuntimeError("Dispatcher is still not registered")
        return self.thrift_service_dispatcher_cls

    def _is_shutting_down(self):
        """
        If gunicorn wants worker to gracefully shutdown, it
        will call `worker_term`(in gunicorn_config.py). We set
        a system env there, and at this place, check that env.
        """
        return os.environ.get('SERVER_SHUTTINGDOWN')

    def _raise_unknown_error(self, exc):
        """
        Help to raise an `unknown_exc` of current service.
        """
        code = self.error_code.UNKNOWN_ERROR
        name = self.error_code._VALUES_TO_NAMES[code]
        raise self.unknown_exc(code, name, repr(exc))

    def run(self, dispatcher, func, args, logger):
        pass
