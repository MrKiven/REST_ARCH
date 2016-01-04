# -*- coding: utf-8 -*-

import yaml
import logging

from .consts import (
    ARCH_CONFIG_PATH,
    ENV_DEV
)


logger = logging.getLogger(__name__)


class ArchConfig(object):
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
