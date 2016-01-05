# -*- coding: utf-8 -*-

import logging
import os
import sys
from .config import load_arch_config, load_app_config
from .exc import AppConfigLoadFailException, EnvNotReadyYetException
from .consts import (
    APP_CONFIG_PATH,
    ENV_DEV,
    ENV_TESTING,
    ENV_PROD
)

logger = logging.getLogger(__name__)


def env():
    return load_arch_config().env


def is_in_dev():
    return load_arch_config().env == ENV_DEV


def is_in_testing():
    return load_arch_config().env == ENV_TESTING


def is_in_prod():
    return load_arch_config().env == ENV_PROD


_is_in_container = None


def is_in_container():
    global _is_in_container
    if _is_in_container is None:
        if os.path.exists(APP_CONFIG_PATH):
            try:
                load_app_config(raise_exc=True)
            except AppConfigLoadFailException:
                _is_in_container = False
            else:
                _is_in_container = True
        else:
            _is_in_container = False
    return _is_in_container

gevent_patched = False
in_profile = False
loggers_initialized = False


def set_profile(v):
    global in_profile
    in_profile = bool(v)


def is_in_profile():
    return in_profile


def require(name):
    if is_in_container() and not globals()[name]:
        raise EnvNotReadyYetException(
            "env not ready: require {}".format(name))


def patch_gevent():
    """Call gevent monkey patch right after ``post_fork``.
    """
    global gevent_patched
    if gevent_patched:
        logger.warn("Gevent is already patched, skipping")
        return
    if 'threading' in sys.modules:
        logger.warn('Threading imported before gevent patching.')
    import gevent.monkey
    gevent.monkey.patch_all()
    gevent_patched = True
