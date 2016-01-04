# -*- coding: utf-8 -*-

import logging
from .config import load_arch_config
from .consts import (
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
