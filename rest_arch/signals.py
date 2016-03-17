# -*- coding: utf-8 -*-

from blinker import signal

before_api_called = signal('before_api_called')
after_api_called = signal('after_api_called')

# TODO add more signals
