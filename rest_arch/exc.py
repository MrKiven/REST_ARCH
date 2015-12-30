# -*- coding: utf-8 -*-


class ServerRestartException(Exception):
    """Raised if a `ping` request incomes but our sever is shutting down."""
    pass


class ArchWarningException(Exception):
    pass


###
# Message's Exc
###

class ArchMessageExc(Exception):
    """ Message base exc """


class BrokersInfoNotFoundExc(ArchMessageExc):
    message = 'Could not found mq\' brokers info in app.yaml'


class ConsumerConfigBadFormatExc(ArchMessageExc):
    message = 'Message consumer\'s config is not correctly formatted ' \
              'in app.yaml.'


class BrokerUrlsNotConfigedExc(ArchMessageExc):
    message = 'Message queue\'s broker urls is not configured in app.yaml'
