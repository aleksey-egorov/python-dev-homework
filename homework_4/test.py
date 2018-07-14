import unittest
import functools
import hashlib
import datetime

import api



def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                print ("\n---\nFunction: {}, Case: {} ".format(f.__name__, c))
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)
        return wrapper
    return decorator


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = None

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).encode('utf-8')).hexdigest()
        else:
            msg = str(request.get("account", "")) + str(request.get("login", "")) + api.SALT
            request["token"] = hashlib.sha512(msg.encode('utf-8')).hexdigest()


    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)


    @cases([
        {"account": "horns&hoofs", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f"},
        {"account": "h12324oofs", "methods": "online_score", "token": "", "arguments": {}},
    ])
    def test_invalid_request(self, request):
        _, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)


    ## Account field tests

    @cases([
        {"login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": "-1", "login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": "1234", "login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_ok_account_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"account": 123, "login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": {1,2}, "login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": ['123','234'], "login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_invalid_account_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code)


    ## Login field tests

    @cases([
        {"account": "admin", "login": "",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"account": "ivan", "login": "-1",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"account": "ivan", "login": "12341",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_ok_login_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"account": "admin", "login": 456,
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": "ivan", "login": {4,5},
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": "ivan", "login": [7,56],
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_invalid_login_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code)


if __name__ == "__main__":
    unittest.main()
