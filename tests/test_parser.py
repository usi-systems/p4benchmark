# -*- coding: utf-8 -*-

import os
import unittest
from subprocess import call

from .context import p4gen

class ParserTests(unittest.TestCase):
    """Parser test cases."""

    def setUp(self):
        self.assertIsNotNone(os.environ.get('P4BENCHMARK_ROOT'))
        self.assertIsNotNone(os.environ.get('PYTHONPATH'))
        pypath = os.environ.get('PYTHONPATH')
        p4bench = os.environ.get('P4BENCHMARK_ROOT')
        self.assertIn(p4bench, p4bench.split(os.pathsep))
        bmv2 = os.path.join(p4bench, 'behavioral-model')
        self.p4c = os.path.join(p4bench, 'p4c-bm/p4c_bm/__main__.py')
        switch_path = os.path.join(bmv2, 'targets/simple_switch/simple_switch')
        cli_path = os.path.join(bmv2, 'tools/runtime_CLI.py')


    def tearDown(self):
        pass

    def test_benchmark_parser_complexity_small(self):
        ret = p4gen.bm_parser.add_number_of_branchings(2, 2)
        self.assertTrue(ret)

    def test_benchmark_parser_complexity_big_fanout(self):
        ret = p4gen.bm_parser.add_number_of_branchings(2, 10)
        self.assertTrue(ret)

    def test_benchmark_parser_complexity_big_depth(self):
        ret = p4gen.bm_parser.add_number_of_branchings(10, 2)
        self.assertTrue(ret)

    def test_benchmark_parser_complexity_big(self):
        ret = p4gen.bm_parser.add_number_of_branchings(5, 5)
        self.assertTrue(ret)
