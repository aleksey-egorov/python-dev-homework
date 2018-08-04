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



    # Functional tests

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
