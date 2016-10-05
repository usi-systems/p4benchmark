# -*- coding: utf-8 -*-

import unittest
import os
from subprocess import call, Popen, PIPE
import shlex
import time
from nose_parameterized import parameterized
from nose.tools import assert_equal

from .context import p4gen

class BenchmarkParser(unittest.TestCase):
    @parameterized.expand([
        (10, 1),
        (20, 1),
        (30, 1),
        (40, 1),
        (50, 1),
        # (60, 1),
        # (70, 1),
        # (80, 1),
        # (90, 1),
        # (100, 1),
    ])

    def test_sequence(self, nb_header, nb_fields):
        ret = p4gen.bm_parser.benchmark_parser(nb_header, nb_fields)
        self.assertTrue(ret)
        # run switch
        self.run_behavioral_switch()
        # run packet generator
        self.run_packet_generator()

    def setUp(self):
        self.assertIsNotNone(os.environ.get('P4BENCHMARK_ROOT'))
        self.assertIsNotNone(os.environ.get('PYTHONPATH'))
        pypath = os.environ.get('PYTHONPATH')
        p4bench = os.environ.get('P4BENCHMARK_ROOT')
        self.assertIn(p4bench, p4bench.split(os.pathsep))
        bmv2 = os.path.join(p4bench, 'behavioral-model')
        self.p4c = os.path.join(p4bench, 'p4c-bm/p4c_bm/__main__.py')
        self.switch_path = os.path.join(bmv2, 'targets/simple_switch/simple_switch')
        self.cli_path = os.path.join(bmv2, 'tools/runtime_CLI.py')
        self.nb_packets = 20000
        # inter-packet gap: 200 us
        self.interval = 200000
        self.log_level = ''

    def tearDown(self):
        cmd = 'sudo pkill lt-simple_swi'
        args = shlex.split(cmd)
        p = Popen(args)
        out, err = p.communicate()
        if out:
            print out
        if err:
            print err
        self.p.wait()
        self.assertIsNotNone(self.p.poll())

    def add_rules(self, json_path, commands, retries):
        if retries > 0:
            cmd = [self.cli_path, '--json', json_path]
            if os.path.isfile(commands):
                with open(commands, "r") as f:
                    p = Popen(cmd, stdin=f, stdout=PIPE, stderr=PIPE)
                    out, err = p.communicate()
                    if out:
                        print out
                        if "Could not" in out:
                            print "Retry in 1 second"
                            sleep(1)
                            return self.add_rules(json_path, port_number, commands, retries-1)
                        elif  "DUPLICATE_ENTRY" in out:
                            pass
                    if err:
                        print err
                        time.sleep(1)
                        return self.add_rules(json_path, port_number, commands, retries-1)

    def run_packet_generator(self):
        cmd = 'sudo {0} -p {1} -i veth4 -c {2} -t {3}'.format('pktgen/build/p4benchmark',
            'output/test.pcap', self.nb_packets, self.interval)
        print cmd
        args = shlex.split(cmd)
        p = Popen(args)
        out, err = p.communicate()
        if out:
            print out
        if err:
            print err
        p.wait()

    def run_behavioral_switch(self):
        prog = 'main'
        json_path = 'output/%s.json' % prog
        commands = 'output/commands.txt'
        ret = call([self.p4c, 'output/%s.p4' % prog , '--json', json_path])
        self.assertEqual(ret, 0)
        cmd = 'sudo {0} {1} -i0@veth0 -i1@veth2 -i 2@veth4 {2}'.format(self.switch_path,
                json_path, self.log_level)
        print cmd
        args = shlex.split(cmd)
        with open('/tmp/bm_switch.log', 'a') as out:
            self.p = Popen(args, stdout=out, stderr=out, shell=False)
    
        self.assertIsNone(self.p.poll())
        # wait for the switch to start
        time.sleep(2)
        # insert rules: retry 3 times if not succeed
        self.add_rules(json_path, commands, 3)



# if __name__ == '__main__':
#     suite = unittest.TestLoader().loadTestsFromTestCase(BenchmarkParser)
#     unittest.TextTestRunner(verbosity=2).run(suite)
