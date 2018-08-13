#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from tests.methods import TestMethods, cases
import api


class TestUnitFieldAccount(TestMethods, unittest.TestCase):

    @cases([
        {"account": None},
        {"account": ""},
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


class TestUnitFieldLogin(TestMethods, unittest.TestCase):

    @cases([
        {"login": ""},
        {"login": "-1"},
        {"login": "12341"},
    ])
    def test_unit_ok_login_field(self, case):
        method = api.MethodRequest()
        method.login.set(case['login'])
        self.assertEqual(case['login'], method.login.value)

    @cases([
        {"login": None},
        {"login": 456},
        {"login": {4, 5}},
        {"login": [7, 56]},
    ])
    def test_unit_bad_login_field(self, case):
        method = api.MethodRequest()
        try:
            method.login.set(case['login'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'login')


class TestUnitFieldMethod(TestMethods, unittest.TestCase):

    @cases([
        {"method": "online_score"},
        {"method": "clients_interests"},
        {"method": "unknown"},
    ])
    def test_unit_ok_method_field(self, case):
        method = api.MethodRequest()
        method.method.set(case['method'])
        self.assertEqual(case['method'], method.method.value)

    @cases([
        {"method": None},
        {"method": ""},
        {"method": 456},
        {"method": {4, 5}},
        {"method": [7, 56]},
    ])
    def test_unit_bad_method_field(self, case):
        method = api.MethodRequest()
        try:
            method.method.set(case['method'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'method')


class TestUnitFieldToken(TestMethods, unittest.TestCase):

    @cases([
        {"token": "fb2e72c45f284600abf73f77024716720fd5a74dd6d738ae4950026b605c34179e19777eb2bd701a75f3f01bc18eeff8fde7d7740852d979213ddcc3d1931265"},
        {"token": ""},
        {"token": "unknown"},
    ])
    def test_unit_ok_token_field(self, case):
        method = api.MethodRequest()
        method.token.set(case['token'])
        self.assertEqual(case['token'], method.token.value)

    @cases([
        {"token": None},
        {"token": 456},
        {"token": {4, 5}},
        {"token": [7, 56]},
    ])
    def test_unit_bad_token_field(self, case):
        method = api.MethodRequest()
        try:
            method.token.set(case['token'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'token')


class TestUnitFieldArguments(TestMethods, unittest.TestCase):

    @cases([
        {"arguments": {"phone": "71112223344"}},
    ])
    def test_unit_ok_arguments_field(self, case):
        method = api.MethodRequest()
        method.arguments.set(case['arguments'])
        self.assertEqual(case['arguments'], method.arguments.value)

    @cases([
        {"arguments": {}},
        {"arguments": None},
        {"arguments": ""},
        {"arguments": 456},
        {"arguments": "unknown"},
        {"arguments": [7, 56]},
    ])
    def test_unit_bad_arguments_field(self, case):
        method = api.MethodRequest()
        try:
            method.arguments.set(case['arguments'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'arguments')


class TestUnitFieldPhone(TestMethods, unittest.TestCase):

    @cases([
         {"phone": "71112223344"},
         {"phone": 70000000000},
         {"phone": ""},
         {"phone": None},
    ])
    def test_unit_ok_phone_field(self, case):
         method = api.OnlineScoreRequest()
         method.phone.set(case['phone'])
         self.assertEqual(case['phone'], method.phone.value)

    @cases([
        {"phone": "81112223344"},
        {"phone": "7111222334"},
        {"phone": 81112223344},
        {"phone": ["71112223344"]},
        {"phone": {}},
    ])
    def test_unit_bad_phone_field(self, case):
        method = api.OnlineScoreRequest()
        try:
            method.phone.set(case['phone'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'phone')


class TestUnitFieldEmail(TestMethods, unittest.TestCase):

    @cases([
        {"email": "123@3.ru"},
        {"email": "123@"},
        {"email": None},
        {"email": ""},
        {"email": "@123.ru"},
    ])
    def test_unit_ok_email_field(self, case):
         method = api.OnlineScoreRequest()
         method.email.set(case['email'])
         self.assertEqual(case['email'], method.email.value)

    @cases([
        {"email": "123.ru"},
        {"email": 8111344},
        {"email": ["71112223344"]},
        {"email": {}},
    ])
    def test_unit_bad_email_field(self, case):
        method = api.OnlineScoreRequest()
        try:
            method.email.set(case['email'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'email')


class TestUnitFieldGender(TestMethods, unittest.TestCase):

    @cases([
        {"gender": None},
        {"gender": ""},
        {"gender": 0},
        {"gender": 1},
        {"gender": 2}
    ])
    def test_unit_ok_gender_field(self, case):
        method = api.OnlineScoreRequest()
        method.gender.set(case['gender'])
        self.assertEqual(case['gender'], method.gender.value)

    @cases([
        {"gender": 4},
        {"gender": -1},
        {"gender": "1"},
        {"gender": [1,2]},
        {"gender": ["71112223344"]},
        {"gender": {}},
    ])
    def test_unit_bad_gender_field(self, case):
        method = api.OnlineScoreRequest()
        try:
            method.gender.set(case['gender'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'gender')


class TestUnitFieldBirthday(TestMethods, unittest.TestCase):

    @cases([
        {"birthday": None},
        {"birthday": ""},
        {"birthday": "01.01.1966"},
        {"birthday": "01.03.2000"},
        {"birthday": "12.12.1950"},
    ])
    def test_unit_ok_birthday_field(self, case):
        method = api.OnlineScoreRequest()
        method.birthday.set(case['birthday'])
        self.assertEqual(case['birthday'], method.birthday.value)

    @cases([
        {"birthday": 11012000},
        {"birthday": "01/01/2000"},
        {"birthday": "2000.01.03"},
        {"birthday": [1,2]},
        {"birthday": ["71112223344"]},
        {"birthday": {}},
        {"birthday": "01.01.1900"},
        {"birthday": "11.11.1920"},
    ])
    def test_unit_bad_birthday_field(self, case):
        method = api.OnlineScoreRequest()
        try:
            method.birthday.set(case['birthday'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'birthday')


class TestUnitFieldFirstname(TestMethods, unittest.TestCase):

    @cases([
        {"first_name": None},
        {"first_name": ""},
        {"first_name": "Ivan"},
        {"first_name": "Ivan2 test"},
    ])
    def test_unit_ok_firstname_field(self, case):
        method = api.OnlineScoreRequest()
        method.first_name.set(case['first_name'])
        self.assertEqual(case['first_name'], method.first_name.value)

    @cases([
        {"first_name": 11012000},
        {"first_name": []},
        {"first_name": ["71112223344"]},
        {"first_name": {}},
    ])
    def test_unit_bad_firstname_field(self, case):
        method = api.OnlineScoreRequest()
        try:
            method.first_name.set(case['first_name'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'first_name')


class TestUnitFieldLastname(TestMethods, unittest.TestCase):

    @cases([
        {"last_name": None},
        {"last_name": ""},
        {"last_name": "Petrov"},
        {"last_name": "Ivan2 test"},
    ])
    def test_unit_ok_lastname_field(self, case):
        method = api.OnlineScoreRequest()
        method.last_name.set(case['last_name'])
        self.assertEqual(case['last_name'], method.last_name.value)

    @cases([
        {"last_name": 1230},
        {"last_name": []},
        {"last_name": ["71112223344"]},
        {"last_name": {}},
    ])
    def test_unit_bad_lastname_field(self, case):
        method = api.OnlineScoreRequest()
        try:
            method.last_name.set(case['last_name'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'last_name')


class TestUnitFieldClientID(TestMethods, unittest.TestCase):

    @cases([
        {"client_ids": [1, 3, 4]},
        {"client_ids": [0]},
    ])
    def test_unit_ok_clientid_field(self, case):
        method = api.ClientsInterestsRequest()
        method.client_ids.set(case['client_ids'])
        self.assertEqual(case['client_ids'], method.client_ids.value)

    @cases([
        {"client_ids": None},
        {"client_ids": -1},
        {"client_ids": 2},
        {"client_ids": "4"},
        {"client_ids": {'id':4}},
        {"client_ids": []},
        {"client_ids": [-2]},
    ])
    def test_unit_bad_clientid_field(self, case):
        method = api.ClientsInterestsRequest()
        try:
            method.client_ids.set(case['client_ids'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'client_ids')


class TestUnitFieldDate(TestMethods, unittest.TestCase):

    @cases([
        {"date": None},
        {"date": ""},
        {"date": "08.07.2017"},
        {"date": "08.07.1917"},
    ])
    def test_unit_ok_date_field(self, case):
        method = api.ClientsInterestsRequest()
        method.date.set(case['date'])
        self.assertEqual(case['date'], method.date.value)

    @cases([
        {"date": -1},
        {"date": 2},
        {"date": "4"},
        {"date": 18072017},
        {"date": "18-07-2017"},
        {"date": "08/07/2017"},
        {"date": "2008.07.17"},
    ])
    def test_unit_bad_date_field(self, case):
        method = api.ClientsInterestsRequest()
        try:
            method.date.set(case['date'])
        except api.ValidationError as err:
            self.assertEqual(err.args[0], 'date')
