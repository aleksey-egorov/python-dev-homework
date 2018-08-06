
import unittest
import functools
import hashlib
import datetime
import requests
import json

import api


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                print("\n---\nFunction: {}, Case: {} ".format(f.__name__, c))
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)

        return wrapper

    return decorator


class TestMethods(unittest.TestCase):

    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = api.Store()

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512(
                (datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).encode('utf-8')).hexdigest()
        else:
            msg = str(request.get("account", "")) + str(request.get("login", "")) + api.SALT
            request["token"] = hashlib.sha512(msg.encode('utf-8')).hexdigest()

    def get_http_response(self, request):
        size = len(str(request))
        session = requests.Session()
        headers = {"Content-Type": "application/json",
                   "Content-Length": str(size)
                   }
        req = requests.Request("post", "http://127.0.0.1:8080/method/", json=request, headers=headers)
        prep = req.prepare()
        resp = session.send(prep)
        response = json.loads(resp.text)
        return response
