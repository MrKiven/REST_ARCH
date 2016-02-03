# -*- coding: utf-8 -*-

import logging
import os
import time
import contextlib
import threading

from sqlalchemy import event

from .consts import PLACE_HOLDER
from .utils import LIB_DIR_PATH

from .skt.config import load_app_config
from .skt import env
from .ctx import g
from .conf import settings


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


#########
# SQL Logging
#########


class SQLLogger(object):
    """SQL logger listens sqlalchemy events on ``engines`` and emits
    logging after ``cursor`` executed::

        sql_logger = SQLLogger()
        sql_logger.register(engine)
    """
    # senstive db field list
    _path = os.path.join(LIB_DIR_PATH, 'static', 'dbsens')
    _content = open(_path).read()
    DB_SENSFIELDS = set(filter(None, _content.splitlines()))

    def __init__(self, name='rest_arch.sql_logger'):
        self.logger = logging.getLogger(name=name)
        env.require('gevent_patched')
        self.ctx = threading.local()
        self.ctx.disable_sql_logging = False
        self.ctx.sql_start_time = None
        self.switch = lambda: False

    def use_switch(self, fn):
        """
        Usage::

            sql_logger.use_switch(lambda: True)  # on
        """
        self.switch = fn

    def register(self, engine):
        event.listen(engine, 'before_cursor_execute',
                     self.before_cursor_execute)
        event.listen(engine, 'after_cursor_execute',
                     self.after_cursor_execute)
        event.listen(engine, 'dbapi_error',
                     self.handle_dbapi_error)
        event.listen(engine, 'commit', self.on_commit)
        event.listen(engine, 'rollback', self.on_rollback)
        event.listen(engine, 'connect', self.on_connect)

    @contextlib.contextmanager
    def disable_sql_logging(self):
        """
        Usage example::

            with sql_logger.disable_sql_logging():
                session.add(User)
                session.commit()
        """
        self.ctx.disable_sql_logging = True
        try:
            yield self
        finally:
            self.ctx.disable_sql_logging = False

    def before_cursor_execute(self, conn, cursor, statement,
                              params, context, executemany):
        if not hasattr(self.ctx, 'disable_sql_logging'):
            self.ctx.disable_sql_logging = False
        self.ctx.sql_start_time = time.time()

    def after_cursor_execute(self, conn, cursor, statement,
                             params, context, executemany):
        self._do_logging(self._get_logging_ctx(conn), statement,
                         params=params, exc=None)

    def handle_dbapi_error(self, conn, cursor, statement,
                           params, context, exception):
        self._do_logging(self._get_logging_ctx(conn), statement,
                         params=params, exc=exception)

    def on_commit(self, conn):
        self._do_logging(self._get_logging_ctx(conn), 'COMMIT')

    def on_rollback(self, conn):
        self._do_logging(self._get_logging_ctx(conn), 'ROLLBACK')

    def on_connect(self, dbapi_conn, conn_record):
        self._do_logging(self._get_logging_ctx_by_dbapi_conn(dbapi_conn),
                         'Connection Open')

    def _get_logging_ctx(self, conn):
        return self._get_logging_ctx_by_dbapi_conn(conn.connection.connection,
                                                   driver=conn.engine.driver)

    def _get_logging_ctx_by_dbapi_conn(self, dbapi_conn, driver=None):
        default = {}.fromkeys(['db', 'host', 'port', 'autocommit'],
                              PLACE_HOLDER)

        if dbapi_conn is None:
            return default

        if driver is None:
            driver = dbapi_conn.__class__.__module__.split('.')[0]

        if driver == 'pymysql':
            return dict(db=dbapi_conn.db,
                        host=dbapi_conn.host,
                        port=dbapi_conn.port,
                        autocommit=dbapi_conn.get_autocommit())
        elif driver == 'psycopg2':
            dct = {}
            for item in dbapi_conn.dsn.split():
                lst = item.split('=')
                dct[lst[0]] = lst[1]
            return dict(db=dct.get('dbname', PLACE_HOLDER),
                        host=dct.get('host', PLACE_HOLDER),
                        port=dct.get('port', PLACE_HOLDER),
                        autocommit=dbapi_conn.autocommit)
        return default

    def _do_logging(self, ctx, statement, params=None, exc=None):
        if not hasattr(self, 'switch') or (
                callable(self.switch) and not self.switch()):
            # there's not a switch or there's a switch and it gives us `off`
            return

        if getattr(self.ctx, 'disable_sql_logging', False):
            # switch is `on` but logging is temply disabled for
            # current thread.
            return

        meta = {}

        # time cost
        cost = None
        if getattr(self.ctx, 'sql_start_time', None) is not None:
            cost = time.time() - self.ctx.sql_start_time
            self.ctx.sql_start_time = None

        if cost is None:
            meta['cost'] = PLACE_HOLDER
        else:
            meta['cost'] = '%.2fms' % (cost * 1000)

        # db instance
        meta['db'] = '{0}/{1}'.format(ctx.get('host', PLACE_HOLDER),
                                      ctx.get('db', PLACE_HOLDER))
        # autocommit
        if 'autocommit' in ctx and ctx['autocommit'] in (False, True):
            meta['ac'] = int(ctx['autocommit'])
        else:
            meta['ac'] = PLACE_HOLDER
        # result
        meta['res'] = exc or 'ok'
        # session id
        meta['session'] = getattr(self.ctx, 'current_session_id', PLACE_HOLDER)

        # filter senstive fields
        statement_list = statement.split()
        has_sens_field = set(statement_list) & SQLLogger.DB_SENSFIELDS
        statement_ = obj2str(' '.join(statement_list))

        if has_sens_field or params is None:
            params_ = PLACE_HOLDER
        else:
            params_ = obj2str(params)

        content = '{0} ## {1}'.format(statement_, params_)

        with logging_meta(**meta):
            if exc is None:
                if cost is None or cost < 1:
                    self.logger.info(content)
                elif 1 <= cost < 5:
                    self.logger.warning(content)
                else:
                    self.logger.error(content)
            else:
                self.logger.error(content)

sql_logger = None


def get_sql_logger():
    global sql_logger
    if sql_logger is None:
        sql_logger = SQLLogger()
        env.require('settings_updated')
        sql_logger.use_switch(settings.SQLLOGGER_SWITCH)
    return sql_logger
