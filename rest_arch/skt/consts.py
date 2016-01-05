# -*- coding: utf-8 -*-

APP_CONFIG_PATH = "app.yaml"
ARCH_CONFIG_PATH = "/etc/rest_arch/env.yaml"

APP_TYPE_BARE = "bare"

HUSKAR_CACHE_DIR = "/var/run/skt_huskar"

DEFAULT_APP_PORT = 8010

DEFAULT_WORKER_NUMBER_DEV = 1
DEFAULT_WORKER_NUMBER_PROD = 2
DEFAULT_WORKER_CLASS = 'gevent'

ENV_DEV = 'dev'
ENV_TESTING = 'testing'
ENV_PROD = 'prod'
