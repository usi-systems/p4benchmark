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
        (5, 1),
        (10, 1),
        (15, 1),
        (20, 1),
        (25, 1),
        (30, 1),
        (35, 1),
        (40, 1),
    ])

    def test_sequence(self, nb_header, nb_fields):
        directory = 'result/parser/headers/{0}'.format(nb_header)
        if not os.path.exists(directory):
            os.makedirs(directory)

        ret = p4gen.bm_parser.benchmark_parser(nb_header, nb_fields)
        self.assertTrue(ret)
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

        out_file = 'result/parser/headers/{0}/latency.csv'.format(nb_header)
        err_file = 'result/parser/headers/{0}/loss.csv'.format(nb_header)
        out = open(out_file, 'w+')
        err = open(err_file, 'w+')
        p = Popen(args, stdout=out, stderr=err)
        p.wait()
        out.close()
        err.close()


    def compile_p4_program(self, nb_header):
        prog = 'main'
        json_path = 'output/%s.json' % prog
        out_file = 'result/parser/headers/{0}/p4c.log'.format(nb_header)
        with open(out_file, 'w+') as out:
            ret = Popen([self.p4c, 'output/%s.p4' % prog , '--json', json_path],
                stdout=out, stderr=out)
            self.assertEqual(ret, 0)

    def run_behavioral_switch(self, nb_header):
        prog = 'main'
        json_path = 'output/%s.json' % prog
        commands = 'output/commands.txt'
        cmd = 'sudo {0} {1} -i0@veth0 -i1@veth2 -i 2@veth4 {2}'.format(self.switch_path,
                json_path, self.log_level)
        print cmd
        args = shlex.split(cmd)
        out_file = 'result/parser/headers/{0}/bmv2.log'.format(nb_header)
        with open(out_file, 'w') as out:
            out.write('Number of packets: %d\n' % self.nb_packets)
            out.write('Inter-packet gap:  %d\n' % self.interval)
            self.p = Popen(args, stdout=out, stderr=out, shell=False)
    
        self.assertIsNone(self.p.poll())
        # wait for the switch to start
        time.sleep(2)
        # insert rules: retry 3 times if not succeed
        self.add_rules(json_path, commands, 3)



# if __name__ == '__main__':
#     suite = unittest.TestLoader().loadTestsFromTestCase(BenchmarkParser)
#     unittest.TextTestRunner(verbosity=2).run(suite)
