# -*- coding: utf-8 -*-

import logging

from importlib import import_module
from .utils import EmptyValue, warn_deprecation

__all__ = ['settings']

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


class NotLoadedError(ConfigError):
    pass


class BaseConfig(object):

    def __init__(self):
        self._settings = {}
        self._loaded = False

    def __getattr__(self, name):
        if not self._loaded:
            raise NotLoadedError('settings not loaded')
        if name not in self._settings:
            raise AttributeError(name)
        return self._settings[name]

    def __setattr__(self, name, value):
        if not self._is_legit_config_name(name):
            return object.__setattr__(self, name, value)
        if self._validate_config_attr(name, value):
            self._settings[name] = value

    def __iter__(self):
        return self._settings.__iter__()

    def _is_legit_config_name(self, name):
        """
        :rtype: bool
        """
        return name.isupper() and '__' not in name

    def _update_config(self, setting_obj, conf_to_update):
        for name in dir(setting_obj):
            if self._is_legit_config_name(name):
                setattr(self, name, getattr(setting_obj, name, None))
        if not self._loaded:
            self._loaded = True
        self._after_update_config()

    def _validate_config_name(self, name, value):
        """
        :rtype: bool
        """
        return self._is_legit_config_name(name)

    def _validate_config_value(self, name, value, type=None):
        """
        :rtype: bool
        """
        if EmptyValue.is_empty(value):
            return False
        if type is not None and issubclass(type, basestring):
            type = basestring
        if type is not None and not isinstance(value, type):
            return False
        return True

    def _validate_config_attr(self, name, value):
        """
        :rtype: bool
        """
        return self._validate_config_name(name, value) and \
            self._validate_config_value(name, value)

    def _after_update_config(self):
        """called after config updated"""
        pass

    def from_object(self, obj):
        """
        :param object obj: an object containing the settings to be loaded, or
                           the name of a package or module to load settings
                           from
        """
        if isinstance(obj, basestring):
            settings_obj = import_module(obj)
        else:
            settings_obj = obj
        self._update_config(settings_obj, self)


def default_empty(val):
    """Make a legal default empty value

    :rtype: :class:`.utils.EmptyValue`

    .. note:: Only use this when empty setting value is possible and
              absolutely tolerable, use plain empty value if a non-empty
              setting value is required
    """
    return EmptyValue(val)


class DefaultConfig(BaseConfig):
    """Load set of default settings defined as ``__DEFAULT_SETTINGS__``
    after initialization
    """
    __DEFAULT_SETTINGS__ = None

    #: ``explicit`` means whether config item other than the ones defined
    #: in ``__DEFAULT_SETTINGS__`` can be imported to expand the settings
    #: items
    explicit = False

    def __init__(self, *args, **kwargs):
        """a config object with default settings provided, note that
        default settings must include the required ones and provide a
        (possibly empty) value with intended data type for each item
        """
        super(DefaultConfig, self).__init__(*args, **kwargs)
        self._make_default()

    def __getattr__(self, name):
        try:
            value = super(DefaultConfig, self).__getattr__(name)
        except NotLoadedError:
            value = self._settings[name]
        if not self._validate_config_attr(name, value):
            raise ConfigError('invalid setting: %r, %r' % (name, value))
        if isinstance(value, EmptyValue):
            return value.val
        return value

    def _validate_config_name(self, name, value):
        if not super(DefaultConfig, self)._validate_config_name(name, value):
            return False
        if self.explicit and name not in self.defaults:
            return False
        return True

    def _validate_config_value(self, name, value, type_=None):
        if isinstance(value, EmptyValue):
            return True
        if name in self.defaults:
            default_config_value = self.defaults[name]
            if isinstance(default_config_value, EmptyValue):
                if isinstance(value, type(default_config_value.val)) and \
                        EmptyValue.is_empty(value):
                    return True
                type_ = type(default_config_value.val)
            else:
                type_ = type(default_config_value)
        return super(DefaultConfig, self)._validate_config_value(name, value,
                                                                 type_)

    def _make_default(self):
        for name, value in self.defaults.iteritems():
            if self._validate_config_name(name, value):
                # bypass __setattr__ check as default value could be
                # empty, will be invalidated later if not overridden
                self._settings[name] = value

    @property
    def defaults(self):
        if self.__DEFAULT_SETTINGS__ is None:
            self.__DEFAULT_SETTINGS__ = {}
        return self.__DEFAULT_SETTINGS__


class CeleryConfig(DefaultConfig):
    """Celery config used by the project's async feature"""
    __DEFAULT_SETTINGS__ = {
        'BROKER_URL': '',
        'CELERY_DEFAULT_EXCHANGE': '',
        'CELERY_RESULT_BACKEND': default_empty(''),
        'CELERY_QUEUES': default_empty({}),
        'CELERYBEAT_SCHEDULE': default_empty({}),

        'BROKER_POOL_LIMIT': 50,
        'CELERY_IMPORTS': ("rest_arch.async"),
        'CELERY_MESSAGE_COMPRESSION': 'gzip',
        'CELERY_REDIS_MAX_CONNECTIONS': 200,
        'CELERY_TASK_RESULT_EXPIRES': 60 * 20,
        'CELERY_TIMEZONE': 'Asia/Shanghai',
        'CELERY_ENABLE_UTC': False,
        'CELERY_ACCEPT_CONTENT': ['pickle', 'msgpack', 'json'],
        'CELERY_TASK_SERIALIZER': 'pickle',
        'CELERY_RESULT_SERIALIZER': 'pickle',
        'CELERYD_MAX_TASKS_PER_CHILD': 5000,
        'CELERY_DISABLE_RATE_LIMITS': True,
        'CELERY_SEND_EVENTS': False,
        'CELERY_SEND_TASK_SENT_EVENT': False,
        'CELERY_TRACK_STARTED': True,
        'CELERY_ACKS_LATE': True,
        'CELERYD_PREFETCH_MULTIPLIER': 1,
        'CELERY_CHORD_PROPAGATES': True,
        'CELERYD_TASK_SOFT_TIME_LIMIT': 10,
        'CELERYD_TASK_TIME_LIMIT': 20,
        'CELERY_TASK_PUBLISH_RETRY': True,
        'CELERY_TASK_PUBLISH_RETRY_POLICY': {
            "max_retries": 10,
            "interval_start": 0,
            "interval_step": 0.2,
            "interval_max": 1,
        },
        'CELERY_DEFAULT_EXCHANGE_TYPE': 'direct',
        'CELERY_ROUTES': ('rest_arch.async.AsyncRouter', ),
    }


class Config(DefaultConfig):
    __DEFAULT_SETTINGS__ = {
        # cache
        'MZDEVICE': '',
        'CACHE_SETTINGS': {},

        # logging
        'SQLLOGGER_SWITCH': lambda: False,

        # async
        'ASYNC_ENABLED': True,
        'ASYNC_CELERYCONFIG': '',
        'USE_MEMORY_MQ': False,
        'TASK_THRIFT_ERROR_RETRY_WAIT': 5,
        'TASK_MAX_RETRY_COUNT': 12 * 60 * 60 / 5,
        'TASK_UNKOWN_ERROR_RETRY_WAIT': 15,
        'TASK_TE_MAX_RETRY_COUNT': 12 * 60 * 60 / 15,
        'TASK_UE_MAX_RETRY_COUNT': 12 * 60 * 60 / 15,


        # db
        'DB_POOL_SIZE': 10,
        'DB_MAX_OVERFLOW': 1,
        'DB_POOL_RECYCLE': 1200,
        'DB_SETTINGS': default_empty({}),
    }
    explicit = True

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

    def _after_update_config(self):
        """if :attr:`ASYNC_ENABLED` is ``True``, will load
        :class:`CeleryConfig`
        """
        super(Config, self)._after_update_config()
        if self.ASYNC_ENABLED and not self.USE_MEMORY_MQ:
            from .skt.config import load_app_config
            self.celeryconfig = CeleryConfig()

            config = load_app_config()
            celery_settings = config.celery_settings
            if not celery_settings:
                warn_deprecation(logger, '`ASYNC_CELERYCONFIG`',
                                 '`celery_settings` in `app.yaml`',
                                 pat='%s is deprecating, use %s instead')
                celery_settings = self.ASYNC_CELERYCONFIG
            self.celeryconfig.from_object(celery_settings)

settings = Config()
