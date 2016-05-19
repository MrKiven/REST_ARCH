# -*- coding: utf-8 -*-

import logging
import os
import sys
from importlib import import_module
from .config import load_arch_config, load_app_config
from .exc import AppConfigLoadFailException, EnvNotReadyYetException
from .log import setup_loggers
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
initialized = False
settings_updated = False


def set_profile(v):
    global in_profile
    in_profile = bool(v)


def is_in_profile():
    return in_profile


def require(name):
    if is_in_container() and not globals()[name]:
        raise EnvNotReadyYetException(
            "env not ready: require {}".format(name))


def initialize():
    """Initialize worker process environment, including: gevent patch,
    settings, signals, logging, client pools etc. It should be called
    before all other operations are taken, right after a worker is forked
    or in cmd entry points. Please note the order of these operations."""
    global initialized
    if initialized:
        logger.warn("Env is already initialized, skipping")
        return
    patch_gevent()
    init_loggers()
    update_settings()
    initialized = True


def init_loggers():
    global loggers_initialized
    if loggers_initialized:
        logger.warn("logging is already initialized, skipping")
        return
    setup_loggers(load_app_config().logger_name, env())
    loggers_initialized = True


def update_settings():
    """Update core's settings by user settings.
    """
    global settings_updated
    if settings_updated:
        logger.warn("settings is already updated, skipping")
        return
    from ..conf import settings
    app_config = load_app_config()
    sys.path.insert(0, '.')
    mo_settings = import_module(app_config.app_settings_uri)
    settings.from_object(mo_settings)
    settings_updated = True


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
