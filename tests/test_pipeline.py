# -*- coding: utf-8 -*-

import unittest
from processing.bm_pipeline import benchmark_pipeline


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_benchmark_pipeline(self):
        ret = benchmark_pipeline(10, 128)
        self.assertTrue(ret)

    def test_benchmark_pipeline_many_tables(self):
        ret = benchmark_pipeline(64, 128)
        self.assertTrue(ret)

    def test_benchmark_pipeline_many_elements(self):
        ret = benchmark_pipeline(2, 65535)
        self.assertTrue(ret)
