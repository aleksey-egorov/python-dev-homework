#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import functools
import hashlib
import datetime
import requests
import json
import time

import api
from store import CacheStore, PersistentStore 
from tests.methods import TestMethods, cases
from tests.test_unit import TestUnitSuite
from tests.test_func import TestFuncSuite

class TestAccSuite(TestMethods):


    # Acceptance tests

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
