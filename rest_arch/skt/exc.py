# -*- coding: utf-8 -*-


class SKTBaseException(Exception):
    """Base Exception for vespene"""


class AppConfigLoadFailException(SKTBaseException):
    """Failed to load app.yaml, not found or yaml invalid"""


class ParameterErrorException(SKTBaseException):
    """Bad parameter"""


class EnvNotReadyYetException(SKTBaseException):
    """Env is not ready yet"""


class WSGIException(SKTBaseException):
    """WSGI related Exception"""
