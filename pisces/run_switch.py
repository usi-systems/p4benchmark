#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from parsing.bm_parser import benchmark_parser_header

class P4Benchmark(object):
    def __init__(self, parent_dir, directory, offer_load):
        assert os.environ.get('P4BENCHMARK_ROOT')
        assert os.environ.get('PYTHONPATH')
        assert os.environ.get('OVS_PATH')
        pypath = os.environ.get('PYTHONPATH')
        p4bench = os.environ.get('P4BENCHMARK_ROOT')
        self.ovs = os.environ.get('OVS_PATH')
        self.dpdk = os.environ.get('DPDK_BUILD')
        bmv2 = os.path.join(p4bench, 'behavioral-model')
        self.p4c = os.path.join(p4bench, 'p4c-bm/p4c_bm/__main__.py')
        self.switch_path = os.path.join(bmv2, 'targets/simple_switch/simple_switch')
        self.cli_path = os.path.join(bmv2, 'tools/runtime_CLI.py')
        self.pktgen = os.path.join(p4bench, 'pktgen/build/p4benchmark')
        self.analyse = os.path.join(p4bench, 'benchmark/analyse.R')
        self.nb_packets = 10000
        self.log_level = ''
        self.parent_dir = parent_dir
        self.directory = directory
        self.offer_load = offer_load

    def run_pisces_switch(self):
        prog = 'main'
        commands = 'output/commands.txt'
        cmd = 'sudo {0} {1} -i0@veth0 -i1@veth2 -i 2@veth4 {2}'.format(self.switch_path,
                json_path, self.log_level)
        print cmd
        args = shlex.split(cmd)
        out_file = '{0}/bmv2.log'.format(self.directory)
        with open(out_file, 'w') as out:
            out.write('Number of packets: %d\n' % self.nb_packets)
            out.write('Offered load:  %d\n' % self.offer_load)
            self.p = Popen(args, stdout=out, stderr=out, shell=False)
        assert (self.p.poll() == None)
        # wait for the switch to start
        time.sleep(2)
        # insert rules: retry 3 times if not succeed
        self.add_rules(json_path, commands, 3)


class BenchmarkParser(P4Benchmark):

    def __init__(self, nb_header, offer_load):
        parent_dir = 'result/headers'
        directory = '{0}/{1}/{2}'.format(parent_dir, nb_header, offer_load)
        super(BenchmarkParser, self).__init__(parent_dir, directory, offer_load)
        self.nb_header = nb_header
        self.nb_field = 1
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def distclean(self):
        cmd = 'sudo make -C {0} distclean'.format(self.ovs)
        p = Popen(shlex.split(cmd))
        p.wait()
        assert (p.returncode == 0)


    def compile_p4_program(self):
        ret = benchmark_parser_header(self.nb_header, self.nb_field)
        assert (ret == True)
        prog = 'main'
        cmd =   """sudo {0}/configure --prefix={0} --with-dpdk={1}
                CFLAGS="-g -O2 -Wno-cast-align"
                p4inputfile={2}
                p4outputdir={0}/include/p4/src""".format(
                self.ovs, self.dpdk, 'output/main.p4')

        print cmd

        out_file = '{0}/pisces_compiler.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen(shlex.split(cmd), stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)

def run(nb_headers=5, step=5):
    offer_load = 100000
    p = BenchmarkParser(nb_headers, offer_load)
    p.compile_p4_program()
    # p.distclean()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-n', '--headers', default=5, type=int,
                        help='number of headers from start')
    parser.add_argument('-s', '--step', default=5, type=int,
                        help='number of headers to add in iteration')
    args = parser.parse_args()

    run(args.headers, args.step)
