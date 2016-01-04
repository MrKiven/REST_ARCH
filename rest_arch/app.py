# -*- coding: utf-8 -*-

from flask import Flask

app_activated = False


##
# make flask app with param config
##
def make_app(**config):
    global app_activated
    try:
        app = Flask(**config)
        return app
    except Exception:
        raise SystemExit("app has not activated!")
    finally:
        app_activated = True


def is_app_activated():
    return app_activated
