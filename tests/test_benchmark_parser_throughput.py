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
        (5, 100000),
        (5, 90000),
        (5, 80000),
        (5, 70000),
        (5, 60000),
        (5, 50000),
        (5, 40000),
        (5, 30000),
        (5, 20000),
        (5, 10000),
        (10, 100000),
        (10, 90000),
        (10, 80000),
        (10, 70000),
        (10, 60000),
        (10, 50000),
        (10, 40000),
        (10, 30000),
        (10, 20000),
        (10, 10000),
        (15, 100000),
        (15, 90000),
        (15, 80000),
        (15, 70000),
        (15, 60000),
        (15, 50000),
        (15, 40000),
        (15, 30000),
        (15, 20000),
        (15, 10000),
        (20, 100000),
        (20, 90000),
        (20, 80000),
        (20, 70000),
        (20, 60000),
        (20, 50000),
        (20, 40000),
        (20, 30000),
        (20, 20000),
        (20, 10000),
        (25, 100000),
        (25, 90000),
        (25, 80000),
        (25, 70000),
        (25, 60000),
        (25, 50000),
        (25, 40000),
        (25, 30000),
        (25, 20000),
        (25, 10000),
        (30, 100000),
        (30, 90000),
        (30, 80000),
        (30, 70000),
        (30, 60000),
        (30, 50000),
        (30, 40000),
        (30, 30000),
        (30, 20000),
        (30, 10000),
        (35, 100000),
        (35, 90000),
        (35, 80000),
        (35, 70000),
        (35, 60000),
        (35, 50000),
        (35, 40000),
        (35, 30000),
        (35, 20000),
        (35, 10000),
        (40, 100000),
        (40, 90000),
        (40, 80000),
        (40, 70000),
        (40, 60000),
        (40, 50000),
        (40, 40000),
        (40, 30000),
        (40, 20000),
        (40, 10000),
    ])

    def test_sequence(self, nb_header, interval):
        directory = 'result/parser/interval/{0}/{1}'.format(nb_header, interval)
        if not os.path.exists(directory):
            os.makedirs(directory)
        ret = p4gen.bm_parser.benchmark_parser(nb_header, 1)
        self.assertTrue(ret)
        self.interval = interval
        # compile
        self.compile_p4_program(nb_header)
        # run switch
        self.run_behavioral_switch(nb_header)
        # run packet generator
        self.run_packet_generator(nb_header)

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
        self.nb_packets = 100000
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
        time.sleep(5)

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

    def run_packet_generator(self, nb_header):
        cmd = 'sudo {0} -p {1} -i veth4 -c {2} -t {3}'.format('pktgen/build/p4benchmark',
            'output/test.pcap', self.nb_packets, self.interval)
        print cmd
        args = shlex.split(cmd)
        out_file = 'result/parser/interval/{0}/{1}/latency.csv'.format(nb_header, self.interval)
        err_file = 'result/parser/interval/{0}/{1}/loss.csv'.format(nb_header, self.interval)
        out = open(out_file, 'w+')
        err = open(err_file, 'w+')
        p = Popen(args, stdout=out, stderr=err)
        p.wait()
        out.close()
        err.close()

    def compile_p4_program(self, nb_header):
        prog = 'main'
        json_path = 'output/%s.json' % prog
        out_file = 'result/parser/interval/{0}/{1}/p4c.log'.format(nb_header, self.interval)
        with open(out_file, 'w+') as out:
            p = Popen([self.p4c, 'output/%s.p4' % prog , '--json', json_path],
                stdout=out, stderr=out)
            p.wait()
            self.assertEqual(p.returncode, 0)

    def run_behavioral_switch(self, nb_header):
        prog = 'main'
        json_path = 'output/%s.json' % prog
        commands = 'output/commands.txt'
        cmd = 'sudo {0} {1} -i0@veth0 -i1@veth2 -i 2@veth4 {2}'.format(self.switch_path,
                json_path, self.log_level)
        print cmd
        args = shlex.split(cmd)
        out_file = 'result/parser/interval/{0}/{1}/bmv2.log'.format(nb_header, self.interval)
        with open(out_file, 'w') as out:
            out.write('Number of packets: %d\n' % self.nb_packets)
            out.write('Inter-packet gap:  %d\n' % self.interval)
            self.p = Popen(args, stdout=out, stderr=out, shell=False)
        self.assertIsNone(self.p.poll())
        # wait for the switch to start
        time.sleep(2)
        # insert rules: retry 3 times if not succeed
        self.add_rules(json_path, commands, 3)