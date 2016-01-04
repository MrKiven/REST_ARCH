"""Plugin to prevent pylint from erroring on zmq imports"""
from astroid import nodes
from astroid import MANAGER
from astroid.builder import AstroidBuilder


def zmq_transform(module):
    """Create a fake zmq module with missing members"""
    if module.name == 'zmq':
        fake = AstroidBuilder(MANAGER).string_build('''

DEALER = None
ROUTER = None
REQ = None
REP = None
PUB = None
SUB = None
PUSH = None
PULL = None
SUBSCRIBE = None
UNSUBSCRIBE = None
NOBLOCK = None

class ZMQError(Exception):
    pass

import zmq.green as zmq
class MySocket(zmq.Socket):
    setsockopt_string = lambda x, y: None
    connect = lambda x: None
    setsockopt = lambda x, y: None
    recv_string = lambda: None
    send_string = lambda x: None

class Context():
    socket = lambda x: MySocket()

''')
        for property in ('Context', 'DEALER', 'ROUTER', 'REQ', 'REP',
                         'PUB', 'SUB', 'PUSH', 'PULL', 'SUBSCRIBE',
                         'UNSUBSCRIBE', 'NOBLOCK', 'ZMQError'):
            module.locals[property] = fake.locals[property]


MANAGER.register_transform(nodes.Module, zmq_transform)


def register(linter):
    pass
