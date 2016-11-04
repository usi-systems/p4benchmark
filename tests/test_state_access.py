# -*- coding: utf-8 -*-

import unittest
from state_access.bm_memory import benchmark_memory

class RegisterTestSuite(unittest.TestCase):
    """Register test cases."""

    def test_generate_multiple_registers(self):
        ret = benchmark_memory(10, 32, 1024, 1)
        self.assertTrue(ret)

    def test_generate_single_register(self):
        ret = benchmark_memory(3, 32, 1024, 10)
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()