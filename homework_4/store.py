import redis


class StoreError(Exception):
    def __init__(self, error):
        self.message = "Store error - {}".format(error)


class Store():
    def __init__(self):
        self.storage = None

    def set_mode(self, mode):
        handler = {
            'persistent': PersistentStore,
            'cache': CacheStore
        }
        try:
            self.storage = handler[mode]()
        except Exception as err:
            raise StoreError(err)


class CacheStore():
    def __init__(self):
        self.conn = redis.StrictRedis(host='', port=6379, password='', encoding='utf-8',
                                      socket_timeout=0.5, socket_connect_timeout=0.4, retry_on_timeout=True, max_connections=3,  db=0)

    def set(self, key, value, time):
        try:
            res = self.conn.set(key, value, ex=time)
            return res
        except:
            pass

    def get(self, key):
        try:
            res = self.conn.get(key)
            return res
        except:
            pass


class PersistentStore():
    def __init__(self):
        self.conn = redis.StrictRedis(host='', port=6379, password='', encoding='utf-8',
                                      socket_timeout=1, socket_connect_timeout=0.8, retry_on_timeout=True, max_connections=10, db=0)

    def set(self, key, value):
        try:
            res = self.conn.set(key, value)
            return res
        except Exception as err:
            raise StoreError(err)

    def get(self, key):
        try:
            res = self.conn.get(key)
            return res
        except Exception as err:
            raise StoreError(err)