# -*- coding: utf-8 -*-

from flask import Flask


##
# make flask app with param config
##
def make_app(**config):
    app = Flask(__name__)
    return app
