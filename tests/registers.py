# -*- coding: utf-8 -*-

from .context import p4gen

import unittest


class RegisterTestSuite(unittest.TestCase):
    """Register test cases."""

    def test_generate_multiple_registers(self):
        ret = p4gen.bm_memory.benchmark_memory(10, 32, 1024, 1)
        self.assertTrue(ret)

    def test_generate_single_register(self):
        ret = p4gen.bm_memory.benchmark_memory(3, 32, 1024, 10)
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()