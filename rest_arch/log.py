# -*- coding: utf-8 -*-

import logging
import contextlib
from .skt.config import load_app_config
from .ctx import g


def obj2str(obj):
    """Try to convert an object to string format."""
    if isinstance(obj, unicode):
        return obj.encode('utf8')
    elif isinstance(obj, (str, int, float, bool)):
        return str(obj)
    return repr(obj)


@contextlib.contextmanager
def logging_meta(**kwargs):
    """Logging with key-value meta, e.g.
    ::

        with logging_meta(key=val) as ctx:
            # do logging
    """
    conflicts = {}
    meta = g.logging_meta

    # if has conflicts, record the original kvs
    for key in kwargs:
        if key in meta:
            conflicts[key] = meta[key]

    try:
        meta.update(kwargs)
        yield meta
    finally:
        # recovery the original conflict kvs
        for key in kwargs:
            meta.pop(key)
        meta.update(conflicts)


class RestFormatter(logging.Formatter):
    """
    Logging formmater with meta (kv pairs) support.

    Skeletal structure::

        [required_meta] extra_meta ## body

    Detail structure::

        datetime level name[pid]: [app_id rpc_id request_id] k => v .. ## msg

    """

    def _format(self, msg):
        # required meta
        app_id = load_app_config().app_id
        request_id = g.get_call_meta('request_id')
        rpc_id = g.get_call_meta('seq')
        required_meta = '[{0} {1} {2}]'.format(app_id, rpc_id, request_id)

        # extra_meta
        metas = [required_meta]
        if g.logging_meta:
            for item in g.logging_meta.iteritems():
                k, v = map(obj2str, item)
                extra_meta = '%s => %s' % (k, v)
                metas.append(extra_meta)

        # meta
        meta = ' '.join(metas)
        # body
        body = obj2str(msg)
        # join msg
        return ' ## '.join([meta, body])

    def format(self, record):
        record.msg = self._format(record.msg)
        return super(RestFormatter, self).format(record)
