import redis
from store_cfg import *


class StoreError(Exception):
    def __init__(self, error):
        self.message = "Store error - {}".format(error)


class Store():
    def __init__(self, **kwargs):
        self.storage = None
        self.kwargs = kwargs

    def set_mode(self, mode):
        handler = {
            'persistent': PersistentStore,
            'cache': CacheStore
        }
        try:
            self.storage = handler[mode](**self.kwargs)
        except Exception as err:
            raise StoreError(err)


class CacheStore():
    def __init__(self, socket_timeout=0.5, socket_connect_timeout=0.5):
        self.conn = redis.StrictRedis(host=store_host, port=6379, password=store_password, encoding='utf-8',
                                      socket_timeout=socket_timeout, socket_connect_timeout=socket_connect_timeout,
                                      retry_on_timeout=True, max_connections=3,  db=0)

    def set(self, key, value, time):
        try:
            return self.conn.set(key, value, ex=time)
        except:
            pass

    def get(self, key):
        try:
            return self.conn.get(key)
        except:
            pass


class PersistentStore():
    def __init__(self, socket_timeout=1, socket_connect_timeout=1):
        self.conn = redis.StrictRedis(host=store_host, port=6379, password=store_password, encoding='utf-8',
                                      socket_timeout=socket_timeout, socket_connect_timeout=socket_connect_timeout,
                                      retry_on_timeout=True, max_connections=10, db=0)

    def set(self, key, value):
        try:
            return self.conn.set(key, value)
        except Exception as err:
            raise StoreError(err)

    def get(self, key):
        try:
            return self.conn.get(key)
        except Exception as err:
            raise StoreError(err)