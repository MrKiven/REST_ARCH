# -*- coding: utf-8 -*-

import os
import sys
from flask import Flask
from werkzeug.serving import WSGIRequestHandler

import rest_arch


##
# make flask app with param config
##
def make_app(name=__package__, **kwargs):
    try:
        return SKT(name, **kwargs)
    except Exception as exc:
        raise SystemExit(exc)


class SKTWSGIRequestHandler(WSGIRequestHandler):
    """ Extend werkzeug request handler to include current Eve version in all
    responses, which is super-handy for debugging.
    """
    @property
    def server_version(self):
        return 'Eve/%s ' % rest_arch.__version__ + \
               super(SKTWSGIRequestHandler, self).server_version


class SKT(Flask):

    def __init__(self, import_name, settings='settings.py',
                 validator=None, data=None, auth=None, redis=None,
                 url_coverters=None, json_encoder=None, media=None,
                 **kwargs):
        super(SKT, self).__init__(import_name, **kwargs)

        self.settings = settings
        self.load_config()

    def run(self, host=None, port=None, debug=None, **options):
        options.setdefault('request_handler', SKTWSGIRequestHandler)
        super(SKT, self).run(host, port, debug, **options)

    def load_config(self):
        # load defaults
        self.config.from_object('rest_arch.settings')

        # overwrite the defaults with custom user settings
        if isinstance(self.settings, dict):
            self.config.update(self.settings)
        else:
            if os.path.isabs(self.settings):
                pyfile = self.settings
            else:
                abspath = os.path.abspath(os.path.dirname(sys.argv[0]))
                pyfile = os.path.join(abspath, self.settings)
            try:
                self.config.from_pyfile(pyfile)
            except IOError:
                # assume envvar is going to be used exclusively
                pass
            except:
                raise
