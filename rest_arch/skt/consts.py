# -*- coding: utf-8 -*-

APP_CONFIG_PATH = "app.yaml"
ARCH_CONFIG_PATH = "/etc/rest_arch/env.yaml"

APP_TYPE_BARE = "bare"

HUSKAR_CACHE_DIR = "/var/run/skt_huskar"

DEFAULT_WORKER_CLASS_WSGI = 'gevent'
DEFAULT_WORKER_NUMBER_DEV = 1
DEFAULT_WORKER_NUMBER_PROD = 2

ENV_DEV = 'dev'
ENV_TESTING = 'testing'
ENV_PROD = 'prod'
