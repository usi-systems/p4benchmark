import os
import unittest
from subprocess import call
from parsing.bm_parser import benchmark_parser_header
from parsing.bm_parser import benchmark_parser_with_header_field
from parsing.bm_parser import parser_complexity

class ParserTests(unittest.TestCase):
    """Parser test cases."""

    def test_benchmark_parser_header(self):
        ret = benchmark_parser_header(10, 1)
        self.assertTrue(ret)

    def test_benchmark_parser_field(self):
        ret = benchmark_parser_with_header_field(10)
        self.assertTrue(ret)

    def test_benchmark_parser_complexity_small(self):
        ret = parser_complexity(2, 2)
        self.assertTrue(ret)

    def test_benchmark_parser_complexity_big_fanout(self):
        ret = parser_complexity(2, 10)
        self.assertTrue(ret)

    def test_benchmark_parser_complexity_medium_depth(self):
        ret = parser_complexity(10, 2)
        self.assertTrue(ret)

    def test_benchmark_parser_complexity_big_depth(self):
        ret = parser_complexity(500, 1)
        self.assertTrue(ret)

    def test_benchmark_parser_complexity_big(self):
        ret = parser_complexity(5, 5)
        self.assertTrue(ret)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ParserTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
