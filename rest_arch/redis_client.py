# -*- coding: utf-8 -*-

from redis import Redis


def create_redis_client(redis_dsn):
    '''Create redis client from dsn uri
    :param redis_dsn: Redis uri, such as "redis://localhost:6383"
    :return: `Redis` instance
    '''
    return Redis.from_url(redis_dsn)


def create_redis_client_from_config(config):
    '''Create redis client from config dict
    :param config: Redis confis, such as {"host": "localhost", "port": 6383}
    :return: `Redis` instance
    '''
    return Redis(**config)
