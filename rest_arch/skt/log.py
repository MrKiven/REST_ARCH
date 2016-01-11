# -*- coding: utf-8 -*-

import logging

from .consts import ENV_DEV


def setup_logger_cls():
    pass


def _gen_console_logging_config(logger_name):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            logger_name: {
                'handlers': ['console'],
                'propagate': False,
                'level': 'INFO',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'console',
            },
        },
        'formatters': {
            'console': {
                '()': 'rest_arch.log.RestFormatter',
                'format': ('%(asctime)s %(levelname)-6s '
                           '%(name)s[%(process)d] %(message)s'),
            },
        },
    }


def _gen_syslog_logging_config(logger_name):
    """Generate logging dict config for production env, if
    ``settings.SENTRY_DSN`` is provided, sentry logging handler will
    be enabled. """
    from .config import load_app_config
    cfg = load_app_config()
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'handlers': ['syslog', 'syslog_udp'],
            'level': 'INFO',
        },
        'loggers': {
            '{}.rest_arch.sql_logger'.format(cfg.app_slug): {
                'handlers': ['syslog_udp'],
                'propagate': False,
                'level': 'INFO',
            },
            logger_name: {
                'handlers': ['syslog'],
                'propagate': False,
                'level': 'INFO',
            },
            'gunicorn.{0}'.format(cfg.app_name): {
                'handlers': ['syslog'],
                'propagate': False,
                'level': 'INFO',
            },
            'gunicorn.{0}.wsgi.access'.format(cfg.app_name): {
                'handlers': ['syslog'],
                'propagate': False,
                'level': 'INFO',
            },
            'gunicorn.{0}.wsgi.error'.format(cfg.app_name): {
                'handlers': ['syslog'],
                'propagate': False,
                'level': 'ERROR',
            },
            '{0}.rest_arch.async'.format(cfg.app_name): {
                'handlers': ['syslog'],
                'propagate': False,
                'level': 'INFO',
            },
        },
        'handlers': {
            'syslog_udp': {
                'level': 'INFO',
                'class': 'logging.handlers.SysLogHandler',
                'address': ('localhost', 514),
                'facility': 'local6',
                'formatter': 'syslog',
            },
            'syslog': {
                'level': 'INFO',
                'class': 'logging.handlers.SysLogHandler',
                'address': '/dev/log',
                'facility': 'local6',
                'formatter': 'syslog',
            },
        },
        'formatters': {
            'syslog': {
                '()': 'rest_arch.log.RestFormatter',
                'format': '%(name)s[%(process)d]: %(message)s',
            },
        },
    }


def gen_logging_dictconfig(logger_name, env):
    if env == ENV_DEV:
        conf = _gen_console_logging_config(logger_name)
    else:
        conf = _gen_syslog_logging_config(logger_name)
    return conf


def setup_loggers(logger_name, env=ENV_DEV):
    setup_logger_cls()
    conf = gen_logging_dictconfig(logger_name, env)
    logging.config.dictConfig(conf)
