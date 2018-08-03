#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.methods import TestMethods, cases
import api

class TestUnitSuite(TestMethods):

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
        {"account": None},
        {"account": "-1"},
        {"account": "1234"},
    ])
    def test_unit_ok_account_field(self, case):
        method = api.MethodRequest()
        method.account.set(case['account'])
        self.assertEqual(case['account'], method.account.value)

    @cases([
        {"account": 123},
        {"account": {1, 2}},
        {"account": ['123', '234']},
    ])
    def test_unit_bad_account_field(self, case):
        method = api.MethodRequest()
        try:
            method.account.set(case['account'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'account')