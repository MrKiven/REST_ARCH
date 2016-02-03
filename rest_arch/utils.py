# -*- coding: utf-8 -*-

import re
import os
import time
import datetime
import hashlib
import uuid
import logging

# used for mobile verify
MOBILE_RE = re.compile('^1[34578]\d{9}$')

ALL_PHONE_RE = re.compile('^1[34578]\d{9}$|^[2-9]\d{6,7}(-\d{1,4})?$'
                          '|^6[1-9]{2,5}$')

# used for email verify
EMAIL_RE = re.compile('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*')

# used for number translate
UNIT_MAP = {u'十': 10, u'百': 100, u'千': 1000, u'万': 10000, u'亿': 100000000}
NUM_MAP = u"零一二三四五六七八九"

# used for capturing timeout error
TServerTimeoutSentryProject = None

# /path/to/rest_arch/rest_arch
LIB_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

DEPRECATION_PATTERN = 'option %r is deprecating, please use %r instead'


def is_mobile(s):
    """
    Check whether a string is mobile number.

    :param s: mobile string to be checked
    """
    return MOBILE_RE.match(s) is not None


def is_phone(s):
    """
    Check whether a string is a fixed phone format.

    :param s: phone string to be checked
    """

    return ALL_PHONE_RE.match(s) is not None


def is_email(s):
    """
    Check whether a string is email address.

    :param s: email string to be checked
    """
    return EMAIL_RE.match(s) is not None


def datetime2utc(dt):
    """
    Sends a :class:`datetime.datetime` object.
    Returns :class:`int` time value.

    :param dt: :class:`datetime` object
    """
    return int(time.mktime(dt.timetuple()))


def utc2datetime(t):
    """
    Sends a :class:`float` time value.
    Returns :class:`datetime.datetime` object.

    :param t: :class:`float` time value.
    """
    return datetime.datetime.fromtimestamp(t)


def strptime2date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def chinese2num(s):
    n = value = unit = flag = 0
    for i in range(len(s)):
        if s[i] in NUM_MAP:
            value = NUM_MAP.index(s[i])
            n += value * unit / 10 if flag and i == len(s) - 1 else value
            flag = 0
        elif s[i] in UNIT_MAP:
            unit = flag = UNIT_MAP[s[i]]
            if unit >= 10000:
                return n * unit + chinese2num(s[i + 1:])
            n += (unit - 1) * value if value else unit
        else:
            raise ValueError
    return n


def md5(s):
    """
    Returns :class:`str` object after md5 encrypt.

    :param s: :class:`str`, the str to md5 encrypt.
    """
    return hashlib.new('md5', s).hexdigest()


def sha1(s):
    """
    Returns :class:`str` object after sha1 encrypt.

    :param s: :class:`str`, the str to sha1 encrypt.
    """
    return hashlib.new('sha1', s).hexdigest()


def get_unique_string(length=31):
    uid = uuid.uuid1()
    full = md5(uid.hex)
    if length > 0:
        return full[:length]
    else:
        return full


class CachedProperty(object):
    """Decorator like python built-in ``property``, but it results only
    once call, set the result into decorated instance's ``__dict__`` as
    a static property.
    """
    def __init__(self, fn):
        self.fn = fn
        self.__doc__ = fn.__doc__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        val = inst.__dict__[self.fn.__name__] = self.fn(inst)
        return val

# alias
cached_property = CachedProperty


class EnvvarReader(dict):
    __uninitialized = object()

    def __init__(self, *envvars):
        for ev in envvars:
            ev_norm = self._normalize(ev)
            if ev != ev_norm:
                raise ValueError(
                    'envvar name should be UPPERCASED: {!r}'.format(ev))
            dict.__setitem__(self, ev_norm, self.__uninitialized)

    @cached_property
    def configured(self):
        return any([self[k] for k in self])

    def _normalize(self, varname):
        return varname.strip().upper()

    def __getitem__(self, key):
        key = self._normalize(key)
        value = dict.__getitem__(self, key)
        if value is self.__uninitialized:
            value = os.getenv(key, None)
            dict.__setitem__(self, key, value)
        return value

    __getattr__ = __getitem__

    def get_int(self, key):
        value = self.__getitem__(key)
        if value is not None:
            return int(value)

    def __setitem__(self, key, value):
        raise RuntimeError('setting envvar not supported')

    __setattr__ = __setitem__


class EmptyValue(object):
    """represent a value that is empty, see :meth:`is_empty` to see what
    empty means here
    """
    def __init__(self, val):
        if not self.is_empty(val):
            raise ValueError('error invalid empty value: %r' % val)
        self.val = val

    @staticmethod
    def is_empty(val):
        """
        empty value means the following stuff:

            ``None``, ``[]``, ``()``, ``{}``, ``''``
        """
        return val not in (False, 0) and not val


def warn_deprecation(logger_or_name, old, new, lvl=logging.WARNING,
                     pat=DEPRECATION_PATTERN):
    if isinstance(logger_or_name, logging.Logger):
        logger = logger_or_name
    else:
        logger = logging.getLogger(logger_or_name)
    logger.log(lvl, pat, old, new)
