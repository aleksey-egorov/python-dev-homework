import redis
import store_cfg




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
            raise api.ValidationError(err)


class CacheStore():
    def __init__(self, host=store_cfg.host, port=store_cfg.port, password=store_cfg.password):
        self.conn = redis.StrictRedis(host=host, port=port, password=password, encoding='utf-8',
                                      socket_timeout=0.5, socket_connect_timeout=0.5,
                                      retry_on_timeout=True, max_connections=3,  db=0)

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
    def __init__(self, host=store_cfg.host, port=store_cfg.port, password=store_cfg.password):
        self.conn = redis.StrictRedis(host=host, port=port, password=password, encoding='utf-8',
                                      socket_timeout=1, socket_connect_timeout=1,
                                      retry_on_timeout=True, max_connections=10, db=0)

    def set(self, key, value):
        try:
            res = self.conn.set(key, value)
            return res
        except Exception as err:
            raise

    def get(self, key):
        try:
            res = self.conn.get(key)
            return res
        except Exception as err:
            raise