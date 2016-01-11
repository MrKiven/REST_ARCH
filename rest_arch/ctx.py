# -*- coding: utf-8 -*-

import threading
from .consts import PLACE_HOLDER
from .skt import env


class ConnCtx(threading.local):
    def __init__(self):
        env.require('gevent_patched')
        super(ConnCtx, self).__init__()
        self.conn_ctx = {}
        self.call_meta_data = {}
        self.logging_meta = {}
        self.user_request_ctx = {}  # user data

    def clear_api_ctx(self):
        self.call_meta_data.clear()
        self.logging_meta.clear()

    def clear_conn_ctx(self):
        self.conn_ctx.clear()

    def clear_user_request_ctx(self):
        self.user_request_ctx.clear()

    def set_call_meta(self, key, value):
        self.call_meta_data[key] = value

    def set_conn_meta(self, key, value):
        self.conn_ctx[key] = value

    def set_user_request_ctx(self, key, value):
        self.user_request_ctx[key] = value

    def get_call_meta(self, key):
        return self.call_meta_data.get(key, PLACE_HOLDER)

    def get_conn_meta(self, key):
        return self.conn_ctx.get(key, PLACE_HOLDER)

    def get_user_request_ctx(self, key):
        return self.user_request_ctx[key]

    def clear_all(self):
        self.clear_api_ctx()
        self.clear_conn_ctx()
        self.clear_user_request_ctx()

g = ConnCtx()
