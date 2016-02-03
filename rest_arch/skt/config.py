# -*- coding: utf-8 -*-

import sys
import yaml
import logging

from .consts import (
    ARCH_CONFIG_PATH,
    APP_CONFIG_PATH,
    APP_TYPE_BARE,
    HUSKAR_CACHE_DIR,
    DEFAULT_APP_PORT,
    DEFAULT_WORKER_CLASS,
    DEFAULT_WORKER_NUMBER_DEV,
    DEFAULT_WORKER_NUMBER_PROD,
    ENV_DEV
)
import rest_arch
from .exc import AppConfigLoadFailException
from ..utils import EnvvarReader, cached_property


logger = logging.getLogger(__name__)


class ArchConfig(object):
    """
    Application independent configs, as a yaml file at
    `CORE_CONFIG_PATH`, example::

        env: 'dev'
        cluster: 'arch-sync-01'
        zookeeper_config:
          hosts: localhost:2181
          username: root
          password:

    """

    def __init__(self):
        self.config = None

    def _load(self, _file):
        try:
            if isinstance(_file, basestring):
                self.config = yaml.load(open(_file))
            else:
                self.config = yaml.load(_file)
        except (IOError, yaml.error.YAMLError):
            logger.warn("cannot load config from %r, useing default", _file)
            self.config = {}

    def load(self, file=None):
        file = file or ARCH_CONFIG_PATH
        self._load(file)
        return self

    @property
    def env(self):
        return self.config.get('env', ENV_DEV)

    @property
    def cluster(self):
        return self.config.get('cluster', None)

arch_config = None


def load_arch_config():
    global arch_config
    if arch_config is None:
        arch_config = ArchConfig().load()
    return arch_config

haproxy_port_map = {}
worker_num_map = {}
port_map = {}


class BareAppConfig(object):
    """Application related configs, as a yaml file at
    `APP_CONFIG_PATH`, e.g.:

        app_name: ves.note
        settings: note.settings
        services:
          wsgi:
            app: note:app
            worker_class: gevent
            requirements: wsgi_requirements.txt
    """

    TYPE_NAME = APP_TYPE_BARE
    PORT_MAP = port_map
    DEFAULT_APP_PORT = None
    DEFAULT_WORKER_CLASS = None

    envvar = EnvvarReader(
        "SKT_APP_PORT",
        "SKT_APP_HAPROXY_PORT",
        "SKT_APP_WORKER_NUM"
    )

    def __init__(self):
        self.config = None

    def load(self, config_path=APP_CONFIG_PATH, raise_exc=False):
        try:
            self.config = yaml.load(open(config_path))
        except (IOError, yaml.error.YAMLError):
            if raise_exc is True:
                raise AppConfigLoadFailException
            logger.error('cannot load %s, exit', config_path)
            sys.exit(1)
        return self

    @cached_property
    def celery_settings(self):
        return self.config.get('celery_settings')

    @cached_property
    def app_name(self):
        return self.config["app_name"]

    @cached_property
    def app_id(self):
        return self.app_name

    @cached_property
    def app_slug(self):
        return self.app_name.rsplit('.', 1)[-1]

    @cached_property
    def app_uri(self):
        app = self._get_conf('app', None)
        if app is None:
            raise RuntimeError("Missing `app` in app.yaml")
        return app

    @cached_property
    def app_settings_uri(self):
        return self.config['settings']

    @cached_property
    def port(self):
        from .env import is_in_dev

        port = self.envvar.get_int('skt_app_port')
        if port:
            return port
        if is_in_dev():
            return self.DEFAULT_APP_PORT
        return self.PORT_MAP.get(self.app_name, self.DEFAULT_APP_PORT)

    @cached_property
    def canonical_port(self):
        from .env import env, is_in_prod

        if not is_in_prod():
            port = self.port
        else:
            port = self.envvar.get_int('skt_app_haproxy_port')
            if not port:
                port = haproxy_port_map.get(self.app_name)
        if not port:
            raise RuntimeError(
                'no canonical port can be determined for app: %r in env: %r'
                % (self.app_name, env()))
        return port

    def get_app_n_workers(self):
        from .env import is_in_prod

        worker_num = self.envvar.get_int('skt_app_worker_num')
        if worker_num:
            return worker_num
        if not is_in_prod():
            return DEFAULT_WORKER_NUMBER_DEV
        return worker_num_map.get(self.app_name, DEFAULT_WORKER_NUMBER_PROD)

    @cached_property
    def worker_class(self):
        return self._get_conf('worker_class', self.DEFAULT_WORKER_CLASS)

    def get_app_binds(self):
        return '0.0.0.0:%d' % self.port

    @cached_property
    def logger_name(self):
        return self.app_name.split('.')[-1]

    @cached_property
    def arch_deps(self):
        with open(self.requirements_file) as f:
            arch_version = None
            for line in f:
                if "rest_arch" in line:
                    arch_version = line.strip()
        return arch_version or "rest_arch==%s" % rest_arch.__version__

    @cached_property
    def message_consumers(self):
        consumers = self.config.get('message_consumer')
        if not consumers:
            raise AppConfigLoadFailException(
                'message.consumer should contains something in app.yaml.')

        return consumers

    @cached_property
    def message_consumers_settings(self):
        return self.config.get('message_consumer_settings', {})

    @cached_property
    def huskar_app_name(self):
        return self.app_name

    @cached_property
    def async_workers(self):
        return self.config.get('async_workers')

    @cached_property
    def requirements_file(self):
        return self.config.get('requirements', 'requirements.txt')

    @cached_property
    def timeout(self):
        return self._get_conf('timeout')

    def get_service_register(self):
        return 'huskar_sdk:ServiceWatcher'

    def get_service_register_conf(self):
        load_arch_config()
        conf = {}
        conf.update(arch_config.zookeeper_config)
        conf.update({
            'team': 'arch',
            'cluster': arch_config.cluster,
            'service_name': self.app_name,
            'cache_dir': HUSKAR_CACHE_DIR,
        })
        return conf

    def _get_conf(self, key, default=None):
        """Help to try config frist on key 'services' and then root.
        """
        if 'services' in self.config and \
                self.TYPE_NAME in self.config['services']:
            return self.config['services'][self.TYPE_NAME].get(key, default)
        return self.config.get(key, default)


class WsgiAppConfig(BareAppConfig):
    TYPE_NAME = "wsgi"
    DEFAULT_APP_PORT = DEFAULT_APP_PORT
    DEFAULT_WORKER_CLASS = DEFAULT_WORKER_CLASS


app_config = None


def load_app_config(raise_exc=False):
    global app_config
    if app_config is None:
        app_config = WsgiAppConfig().load(raise_exc=raise_exc)
    return app_config
