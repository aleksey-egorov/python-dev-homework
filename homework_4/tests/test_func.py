#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.methods import TestMethods, cases
import api

class TestFuncSuite(TestMethods):

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
    def test_func_ok_account_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)

    @cases([
        {"account": 123, "login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": {1, 2}, "login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": ['123', '234'], "login": "h&f",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_func_invalid_account_field(self, request):
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
    def test_func_ok_login_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)

    @cases([
        {"account": "admin", "login": 456,
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": "ivan", "login": {4, 5},
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"account": "ivan", "login": [7, 56],
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_func_invalid_login_field(self, request):
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
         "arguments": {"client_ids": [6, 7], "date": "20.07.2017"}},
    ])
    def test_func_ok_method_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)

    @cases([

        {"account": "ivan", "login": "87687t8g",
         "method": "unknown",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_func_invalid_method_field(self, request):
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
    def test_func_null_method_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_NULLABLE_ERROR])

    @cases([
        {"account": "admin", "login": "fyt54e",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
    ])
    def test_func_no_method_field(self, request):
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
    def test_func_ok_token_field(self, request):
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
    def test_func_invalid_token_field(self, request):
        response, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code)
        self.assertRegex(response.get("message"), api.ERRORS[api.FORBIDDEN])

    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "123@123.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_func_null_token_field(self, request):
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
    def test_func_invalid_arguments_field(self, request):
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
    def test_func_req_arguments_field(self, request):
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
    def test_func_ok_phone_field(self, request):
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
    def test_func_invalid_phone_field(self, request):
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
    def test_func_ok_email_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)

    @cases([
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233.ru", "gender": 1, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_func_wrong_email_field(self, request):
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
    def test_func_invalid_email_field(self, request):
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
    def test_func_ok_gender_field(self, request):
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
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": [1, 2], "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},
        {"login": "ivan",
         "method": "online_score",
         "arguments": {"phone": "71112223344", "email": "1233@3.ru", "gender": {}, "birthday": "01.01.2000",
                       "first_name": "Ivan", "last_name": "Petrov"}},

    ])
    def test_func_invalid_gender_field(self, request):
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
    def test_func_wrong_gender_field(self, request):
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
    def test_func_ok_birthday_field(self, request):
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
    def test_func_invalid_birthday_field(self, request):
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
    def test_func_wrong_birthday_field(self, request):
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
    def test_func_ok_firstname_field(self, request):
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
    def test_func_invalid_firstname_field(self, request):
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
    def test_func_ok_lastname_field(self, request):
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
    def test_func_invalid_lastname_field(self, request):
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
         "arguments": {"client_ids": [1, 2]}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [1, 3, 4]}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [0]}},
    ])
    def test_func_ok_client_ids_field(self, request):
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
         "arguments": {"client_ids": {'id': '6'}}},
    ])
    def test_func_invalid_client_ids_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_LIST_ERROR])

    @cases([
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": []}},
    ])
    def test_func_null_client_ids_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_NULLABLE_ERROR])

    @cases([
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [-4, 7]}},
        {"login": "ivan",
         "method": "clients_interests",
         "arguments": {"client_ids": [7, -1, 2]}},
    ])
    def test_func_negative_client_ids_field(self, request):
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
    def test_func_ok_interests_date_field(self, request):
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
    def test_func_invalid_interests_date_field(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.FIELD_DATE_ERROR])
