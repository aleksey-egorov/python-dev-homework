#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import tests.test_unit as test_unit
import tests.test_func as test_func
import tests.test_acc as test_acc


def start_tests():

    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(test_unit)
    suite.addTests(loader.loadTestsFromModule(test_func))
    suite.addTests(loader.loadTestsFromModule(test_acc))

    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)


if __name__ == "__main__":
     start_tests()

