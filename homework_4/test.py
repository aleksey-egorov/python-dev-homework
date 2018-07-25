import unittest
import functools
import hashlib
import datetime
import requests
import json
import time

import api
from store import CacheStore, PersistentStore



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
        self.store = api.Store()

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).encode('utf-8')).hexdigest()
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



    ## Common tests

    def test_unit_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)


    @cases([
        {"account": "horns&hoofs", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f"},
        {"account": "h12324oofs", "methods": "online_score", "token": "", "arguments": {}},
    ])
    def test_unit_invalid_request(self, request):
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
    def test_unit_ok_account_field(self, request):
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
    def test_unit_invalid_account_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.ERRORS[api.INVALID_REQUEST])


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
    def test_unit_ok_login_field(self, request):
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
    def test_unit_invalid_login_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.ERRORS[api.INVALID_REQUEST])
        self.assertRegex(response.get("message"), 'login')


    ## Method field tests

    @cases([
         {"account": "admin", "login": "5675",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"account": "ivan", "login": "-1",
          "method": "clients_interests",
          "arguments": {"client_ids": [6,7], "date": "20.07.2017"}},
    ])
    def test_unit_ok_method_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([

        {"account": "ivan", "login": "87687t8g",
         "method": "unknown",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_invalid_method_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.REQUEST_BAD_HANDLER_ERROR])


    @cases([
        {"account": "ivan", "login": "85uyg",
         "method": "",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_null_method_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_NULLABLE_ERROR])


    @cases([
        {"account": "admin", "login": "fyt54e",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_no_method_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_REQUIRED_ERROR])


    ## Token field tests

    @cases([
         {"login": "ivan",
          "method": "online_score",
          "token": "fb2e72c45f284600abf73f77024716720fd5a74dd6d738ae4950026b605c34179e19777eb2bd701a75f3f01bc18eeff8fde7d7740852d979213ddcc3d1931265",
          "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"account": "ivan", "login": "ivan1",
           "token": "9ce4596ad0cdd2f2f24d6e6fc534a2f9d6cdfe481e8755558c9dfd349fec4bd6776f44c19ff8f780325c6c38112d811edb5dd2d05158f6c9a8ae9698e1ba6f56",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_ok_token_field(self, request):
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"account": "ivan", "login": "ivan1",
         "token": "05158f6c9a8ae9698e1ba6f56",
         "method": "clients_interests",
         "arguments": {"client_ids": [6, 7], "date": "20.07.2017"}},
        {"login": "ivan",
         "method": "online_score",
         "token": "",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_invalid_token_field(self, request):
        response, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code)
        self.assertRegex(response.get("message"), api.ERRORS[api.FORBIDDEN])


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_unit_null_token_field(self, request):
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.ERRORS[api.INVALID_REQUEST])


    ## Arguments field test

    @cases([
        {"account": "admin", "login": "test",
         "method": "online_score",
         "arguments": "phone"},
        {"account": "ivan", "login": "test",
         "method": "online_score",
         "arguments": 3},
        {"account": "ivan", "login": "test",
         "method": "online_score",
         "arguments": -6},
    ])
    def test_unit_invalid_arguments_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.ERRORS[api.INVALID_REQUEST])
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_ARG_ERROR])
        self.assertRegex(response.get("message"), 'arguments')

    @cases([
        {"account": "ivan", "login": "test",
         "method": "online_score"},
    ])
    def test_unit_req_arguments_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.ERRORS[api.INVALID_REQUEST])
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_REQUIRED_ERROR])
        self.assertRegex(response.get("message"), 'arguments')


    ## Phone field tests

    @cases([
         {"login": "ivan",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": 70000000000, "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_ok_phone_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "81112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "7111222334", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": 81112223344, "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": ["71112223344"], "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": {}, "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_invalid_phone_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_PHONE_ERROR])


    ## Email field tests

    @cases([
         {"login": "ivan",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_ok_email_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_unit_wrong_email_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_EMAIL_ERROR])


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": 123, "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": [], "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": {}, "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_invalid_email_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_CHAR_ERROR])



    ## Gender field tests

    @cases([
         {"login": "ivan",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@3.ru", "gender": 0, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 2, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "@123.ru", "gender": "", "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "@123.ru", "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_unit_ok_gender_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": "1", "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": [1,2], "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": {}, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_unit_invalid_gender_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_NUMERIC_ERROR])


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": 3, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": -1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_unit_wrong_gender_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_GENDER_ERROR])


    ## Birthday field tests

    @cases([
         {"login": "ivan",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@3.ru", "gender": 0, "birthday": "01.01.1966",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 1, "birthday": "01.03.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 2, "birthday": "12.12.1950",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 2, "birthday": "",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_unit_ok_birthday_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": 1, "birthday": 11012000,
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": 1, "birthday": "01/01/2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": 1, "birthday": "2000.01.03",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_unit_invalid_birthday_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_DATE_ERROR])


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": 1, "birthday": "01.01.1900",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": 1, "birthday": "11.11.1920",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_unit_wrong_birthday_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_BIRTHDAY_ERROR])


    ## First name field tests

    @cases([
         {"login": "ivan",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan2 test", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                        "last_name": "Petrov"}},
    ])
    def test_unit_ok_firstname_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": 123, "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": [], "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": {}, "last_name": "Petrov"}},
    ])
    def test_unit_invalid_firstname_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_CHAR_ERROR])


    ## Last name field tests

    @cases([
         {"login": "ivan",
          "method": "online_score",
          "arguments": {"phone": "71112223344", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov2 test"}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": ""}},
         {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "70000000000", "email": "123@3.ru", "gender": 1, "birthday": "01.01.2000",
                        "first_name": "Ivan"}},
    ])
    def test_unit_ok_lastname_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": 1234}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": []}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": {}}},
    ])
    def test_unit_invalid_lastname_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_CHAR_ERROR])


   ## Client ID field tests

    @cases([
         {"login": "ivan",
          "method": "clients_interests",
          "arguments": {"client_ids": [1]}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [1]}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [1]}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [1]}},
    ])
    def test_unit_ok_client_ids_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": -5}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": 7}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": "7"}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": ""}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": {'id':'6'}}},
    ])
    def test_unit_invalid_client_ids_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_LIST_ERROR])


    @cases([
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": []}},
    ])
    def test_unit_null_client_ids_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_NULLABLE_ERROR])


    @cases([
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [-4,7]}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [7, -1, 2]}},
    ])
    def test_unit_negative_client_ids_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_IDS_ERROR])


    ## Date field tests

    @cases([
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [4, 7], "date": "08.07.2017"}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [4, 7], "date": ""}},

    ])
    def test_unit_ok_interests_date_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)


    @cases([
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [4, 7], "date": 18072017}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [4, 7], "date": "18-07-2017"}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [4, 7], "date": "08/07/2017"}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [4, 7], "date": "2008.07.17"}},

    ])
    def test_unit_invalid_interests_date_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_DATE_ERROR])


    ## Store tests

    @cases([
        {"test": "test value"},
        {"test": "Тестовое значение"},
    ])
    def test_unit_ok_cache_store(self, case):
        storage = CacheStore()
        key = list(case.keys())[0]
        storage.set(key, case[key], 60)
        val = storage.get(key)
        self.assertEqual(val.decode('utf-8'), case[key])

    @cases([
        {"test": "test value"},
        {"test": "Тестовое значение"},
    ])
    def test_unit_ok_persistent_store(self, case):
        storage = PersistentStore()
        key = list(case.keys())[0]
        storage.set(key, case[key])
        val = storage.get(key)
        self.assertEqual(val.decode('utf-8'), case[key])

    @cases([
        {"test": "test value"},
    ])
    def test_unit_invalid_cache_store(self, case):
        # Устанавливаем очень низкий timeout для эмуляции отсутствия связи с хранилищем
        storage = CacheStore(socket_timeout=0.001, socket_connect_timeout=0.001)
        key = list(case.keys())[0]
        storage.set(key, case[key], 60)
        val = storage.get(key)
        self.assertEqual(val, None)

    @cases([
        {"test": "test value"},
    ])
    def test_unit_invalid_persistent_store(self, case):
        # Устанавливаем очень низкий timeout для эмуляции отсутствия связи с хранилищем
        storage = PersistentStore(socket_timeout=0.001, socket_connect_timeout=0.001)
        key = list(case.keys())[0]
        try:
            storage.set(key, case[key])
            val = storage.get(key)
        except Exception as error:
            self.assertRegex(error.message, "Timeout connecting to server")

    @cases([
        {"test": "test value"},
    ])
    def test_unit_expired_cache_store(self, case):
        storage = CacheStore()
        key = list(case.keys())[0]
        storage.set(key, case[key], 1) # Записываем значение с минимальным сроком хранения - 1 сек
        time.sleep(1)
        val = storage.get(key) # Значение должно быть пустым
        self.assertEqual(val, None)



    #### Functional tests

    ## Bad auth test

    @cases([
        {"login": "ivan",
         "method": "online_score",
         "token": "fb2e77c45f284600abf73f77024716720fd5a74dd6d738ae4950026b605c34179e19777eb2bd701a75f3f01bc18eeff8fde7d7740852d979213ddcc3d1931265",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": "ivan", "login": "ivan5",
         "token": "9ce4596ad0cdd2f2f24d6e6fc534a2f9d6cdfe481e8755558c9dfd349fec4bd6776f44c19ff8f780325c6c38112d811edb5dd2d05158f6c9a8ae9698e1ba6f56",
         "method": "clients_interests",
         "arguments": {"client_ids": [6, 7], "date": "20.07.2017"}},
    ])
    def test_func_bad_auth(self, request):
        response, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.REQUEST_AUTH_ERROR])


    ## Argument pairs error

    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112344444", "gender": 1}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"email": "123@3.ru", "birthday": "01.01.2000"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"email": "123@3.ru", "gender": 1}},
    ])
    def test_func_argument_pairs(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.REQUEST_ARG_ERROR])


    ## Online score calculation test

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score",
         "arguments": {"gender": 1, "birthday": "01.01.2000"}},
    ])
    def test_func_online_score(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)
        self.assertGreaterEqual(response.get("score"), 0)


    ## Interests search test

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests",
         "arguments": {"client_ids": [1, 2]}},
    ])
    def test_func_client_interests(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)
        self.assertEqual(self.context.get("nclients"), len(request["arguments"]["client_ids"]))
        self.assertEqual(len(request["arguments"]["client_ids"]), len(response))
        self.assertTrue(all(v and isinstance(v, list) and all(isinstance(i, str) for i in v)
                            for v in response.values()))


    ## Persistent store failure test

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests",
         "arguments": {"client_ids": [1, 2]}},
    ])
    def test_func_invalid_persistent_store(self, request):
            self.set_valid_auth(request)
            # Устанавливаем очень низкий timeout для эмуляции отсутствия связи с хранилищем
            self.store = api.Store(socket_timeout=0.001, socket_connect_timeout=0.001)
            response, code = self.get_response(request)
            self.assertEqual(api.INTERNAL_ERROR, code)
            message = response.get("message")
            self.assertRegex(message, "Store error")
            self.assertRegex(message, "Timeout connecting to server")



    #### Acceptance tests

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score",
         "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
         "arguments": {"phone": "75556664455", "email": "aaa@bbb.ru", "gender": 1, "birthday": "11.01.1980",
                       "first_name": "Ivan", "last_name": "Sergeev"}},
    ])
    def test_acc_online_score_score50(self, request):
        response = self.get_http_response(request)
        self.assertEqual(api.OK, response.get("code"))
        self.assertEqual(response.get("response").get("score"), 5.0)

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score",
         "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
         "arguments": {"phone": "78883334455", "email": "aaa@bbb.ru", "birthday": "21.01.2000",
                       "first_name": "John", "last_name": "Smith"}},
    ])
    def test_acc_online_score_score35(self, request):
        response = self.get_http_response(request)
        self.assertEqual(api.OK, response.get("code"))
        self.assertEqual(response.get("response").get("score"), 3.5)

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score",
         "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
         "arguments": {"phone": "72223334455", "email": "aaa@bbb.ru", "birthday": "01.03.2005",
                       "first_name": "aaaa"}},
    ])
    def test_acc_online_score_score30(self, request):
        response = self.get_http_response(request)
        self.assertEqual(api.OK, response.get("code"))
        self.assertEqual(response.get("response").get("score"), 3.0)

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score",
         "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
         "arguments": {"gender": 1, "birthday": "01.01.2006"}},
    ])
    def test_acc_online_score_score20(self, request):
        response = self.get_http_response(request)
        self.assertEqual(api.OK, response.get("code"))
        self.assertEqual(response.get("response").get("score"), 1.5)

    @cases([
        {"account": "horns&hoofs", "login": "admin", "method": "online_score",
         "token": "ef70333170e882478cbaaa97fb07b613a02213e14e0a9094c4a6e0882f10bb505cd1f56ab4cf1707ddc374ae3b2e9bec2d90bc10b4f65bf744dae494b775ad6e",
         "arguments": {"phone": "71113334455", "email": "aaa@bbb.ru", "birthday": "01.01.2000",
                       "first_name": "a"}},
    ])
    def test_acc_online_score_admin(self, request):
        # Токен генерируется автоматически для удобства тестирования. В реальных условиях срок жизни токена админа - один час
        self.set_valid_auth(request)
        response = self.get_http_response(request)
        self.assertEqual(api.OK, response.get("code"))
        self.assertEqual(response.get("response").get("score"), 42)

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests",
         "arguments": {"client_ids": [1]},
         "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95"},
        {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests",
         "arguments": {"client_ids": [1, 2]},
         "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95"},
        {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests",
         "arguments": {"client_ids": [1, 2, 3, 4, 5]},
         "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95"},
    ])
    def test_acc_client_interests_1(self, request):
        response = self.get_http_response(request)
        self.assertEqual(api.OK, response.get("code"))
        self.assertEqual(len(request["arguments"]["client_ids"]), len(response.get('response')))
        self.assertTrue(all(v and isinstance(v, list) and all(isinstance(i, str) for i in v)
                            for v in response.get('response').values()))


if __name__ == "__main__":
    unittest.main()
