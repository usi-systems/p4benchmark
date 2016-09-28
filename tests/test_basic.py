# -*- coding: utf-8 -*-

from .context import p4gen

import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_benchmark_parser(self):
        ret = p4gen.bm_parser.benchmark_parser(10, 4)
        self.assertTrue(ret)

    def test_benchmark_pipeline(self):
        ret = p4gen.bm_pipeline.benchmark_pipeline(10, 128)
        self.assertTrue(ret)

    def test_benchmark_memory_consumption(self):
        ret = p4gen.bm_memory.benchmark_memory(10, 32, 1024)
        self.assertTrue(ret)

    def test_benchmark_add_header(self):
        ret = p4gen.bm_modification.benchmark_modification(10, 4, 'add')
        self.assertTrue(ret)

    def test_benchmark_remove_header(self):
        ret = p4gen.bm_modification.benchmark_modification(10, 4, 'rm')
        self.assertTrue(ret)

    def test_benchmark_modify_header(self):
        ret = p4gen.bm_modification.benchmark_modification(10, 4, 'mod')
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()