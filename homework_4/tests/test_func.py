#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import unittest
from store import CacheStore, PersistentStore
from tests.methods import TestMethods, cases
import api


class TestFuncCommon(TestMethods, unittest.TestCase):

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


class TestFuncStore(TestMethods, unittest.TestCase):

    @cases([
        {"test": "test value"},
        {"test": "Тестовое значение"},
    ])
    def test_ok_cache_store(self, case):
        storage = CacheStore()
        key = list(case.keys())[0]
        storage.set(key, case[key], 60)
        val = storage.get(key)
        self.assertEqual(val.decode('utf-8'), case[key])

    @cases([
        {"test": "test value"},
        {"test": "Тестовое значение"},
    ])
    def test_ok_persistent_store(self, case):
        storage = PersistentStore()
        key = list(case.keys())[0]
        storage.set(key, case[key])
        val = storage.get(key)
        self.assertEqual(val.decode('utf-8'), case[key])

    @cases([
        {"test": "test value"},
    ])
    def test_invalid_cache_store(self, case):
        storage = CacheStore(host="localhost") # Попытка соединения с несуществующим хранилищем
        key = list(case.keys())[0]
        storage.set(key, case[key], 60)
        val = storage.get(key)
        self.assertEqual(val, None)

    @cases([
        {"test": "test value"},
    ])
    def test_invalid_persistent_store(self, case):
        storage = PersistentStore(host="localhost") # Попытка соединения с несуществующим хранилищем
        key = list(case.keys())[0]
        val = None
        try:
            storage.set(key, case[key])
            val = storage.get(key)
        except:
            self.assertRaises(ConnectionError)
        else:
            self.assertEqual(val, case[key])  # Это вызовет ошибку теста если Exception не сработал

    @cases([
        {"test": "test value"},
    ])
    def test_expired_cache_store(self, case):
        storage = CacheStore()
        key = list(case.keys())[0]
        storage.set(key, case[key], 1) # Записываем значение с минимальным сроком хранения - 1 сек
        time.sleep(1)
        val = storage.get(key) # Значение должно быть пустым
        self.assertEqual(val, None)


class TestFuncAuth(TestMethods, unittest.TestCase):

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
    def test_bad_auth(self, request):
        response, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.REQUEST_AUTH_ERROR])


class TestFuncSpecificFields(TestMethods, unittest.TestCase):

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
    def test_argument_pairs(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertRegex(response.get("message"), api.FIELD_REQUEST_ERRORS[api.REQUEST_ARG_ERROR])


class TestFuncCalculations(TestMethods, unittest.TestCase):

    ## Online score calculation test
    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score",
         "arguments": {"gender": 1, "birthday": "01.01.2000"}},
    ])
    def test_online_score(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)
        self.assertGreaterEqual(response.get("score"), 0)

    ## Interests search test
    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests",
         "arguments": {"client_ids": [1, 2]}},
    ])
    def test_client_interests(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)
        self.assertEqual(self.context.get("nclients"), len(request["arguments"]["client_ids"]))
        self.assertEqual(len(request["arguments"]["client_ids"]), len(response))
        self.assertTrue(all(v and isinstance(v, list) and all(isinstance(i, str) for i in v)
                            for v in response.values()))

