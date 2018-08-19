import redis
import store_cfg




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
            raise api.ValidationError(err)


class CacheStore():
    def __init__(self, host=store_cfg.host, port=store_cfg.port, password=store_cfg.password):
        self.conn = redis.StrictRedis(host=host, port=port, password=password, encoding='utf-8',
                                      socket_timeout=0.5, socket_connect_timeout=0.5,
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
    def __init__(self, host=store_cfg.host, port=store_cfg.port, password=store_cfg.password):
        self.conn = redis.StrictRedis(host=host, port=port, password=password, encoding='utf-8',
                                      socket_timeout=1, socket_connect_timeout=1,
                                      retry_on_timeout=True, max_connections=10, db=0)

    def set(self, key, value):
        try:
            return self.conn.set(key, value)
        except:
            raise ConnectionError

    def get(self, key):
        try:
            return self.conn.get(key)
        except:
            raise ConnectionError