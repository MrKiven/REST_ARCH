# -*- coding: utf-8 -*-

import requests
import json


##
# http client
##
class Client(object):

    def __init__(self, host, port):
        self.url = "http://{}:{}".format(host, port)

    def get(self, route):
        return requests.get(self.url + route)

    def post(self, route, payload):
        return requests.post(self.url + route, data=json.dumps(payload))
