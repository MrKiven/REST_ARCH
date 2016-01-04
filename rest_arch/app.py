# -*- coding: utf-8 -*-

from flask import Flask


##
# make flask app with param config
##
def make_app(name, **config):
    global _app_activated
    try:
        _app_activated = True
        return Flask(name, **config)
    except Exception as exc:
        raise SystemExit(exc)
