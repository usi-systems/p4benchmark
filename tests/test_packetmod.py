# -*- coding: utf-8 -*-

import unittest
from packet_modification.bm_modification import benchmark_modification


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_benchmark_add_header(self):
        ret = benchmark_modification(10, 4, 'add')
        self.assertTrue(ret)

    def test_benchmark_add_many_header(self):
        ret = benchmark_modification(32, 4, 'add')
        self.assertTrue(ret)

    def test_benchmark_remove_header(self):
        ret = benchmark_modification(10, 4, 'rm')
        self.assertTrue(ret)

    def test_benchmark_remove_many_header(self):
        ret = benchmark_modification(32, 4, 'rm')
        self.assertTrue(ret)
