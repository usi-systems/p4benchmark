# -*- coding: utf-8 -*-

import unittest
from parsing.bm_parser import benchmark_parser, add_number_of_branchings
from processing.bm_pipeline import benchmark_pipeline
from state_access.bm_memory import benchmark_memory
from packet_modification.bm_modification import benchmark_modification


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_benchmark_parser(self):
        ret = benchmark_parser(10, 4)
        self.assertTrue(ret)

    def test_benchmark_pipeline(self):
        ret = benchmark_pipeline(10, 128)
        self.assertTrue(ret)

    def test_benchmark_memory_consumption(self):
        ret = benchmark_memory(10, 32, 1024, 1)
        self.assertTrue(ret)

    def test_benchmark_add_header(self):
        ret = benchmark_modification(10, 4, 'add')
        self.assertTrue(ret)

    def test_benchmark_remove_header(self):
        ret = benchmark_modification(10, 4, 'rm')
        self.assertTrue(ret)

    def test_benchmark_modify_header(self):
        ret = benchmark_modification(10, 4, 'mod')
        self.assertTrue(ret)