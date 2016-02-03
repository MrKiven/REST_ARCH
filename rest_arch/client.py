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

    # default content-type: json
    def post(self, route, payload, json_format=True):
        if json_format:
            headers = {'Content-Type': 'application/json'}
        else:
            headers = None
        return requests.post(
            self.url + route,
            headers=headers,
            data=json.dumps(payload)
        )

clients = {
    'skt.test': Client('localhost', 8010)
}
