#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from packet_modification.bm_modification import benchmark_modification
from benchmark.benchmark import P4Benchmark

class BenchmarkHeaderRemoval(P4Benchmark):

    def __init__(self, nb_header, nb_field, offer_load):
        parent_dir = 'result/rm_header'
        directory = '{0}/{1}/{2}'.format(parent_dir, nb_header, offer_load)
        super(BenchmarkHeaderRemoval, self).__init__(parent_dir, directory, offer_load)
        self.nb_header = nb_header
        self.nb_field = nb_field
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def compile_p4_program(self):
        ret = benchmark_modification(self.nb_header, self.nb_field, 'rm')
        assert (ret == True)
        prog = 'main'
        json_path = 'output/%s.json' % prog
        out_file = '{0}/p4c.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen([self.p4c, 'output/%s.p4' % prog , '--json', json_path],
                stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)

def run(nb_headers=2, nb_fields=2, step=2):
    while(nb_headers <= 40):
        offer_load = 100000
        p = BenchmarkHeaderRemoval(nb_headers, nb_fields, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = BenchmarkHeaderRemoval(nb_headers, nb_fields, offer_load)
            p.start()

        nb_headers += step
    p.run_analyser()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-n', '--headers', default=4, type=int,
                        help='number of headers from start')
    parser.add_argument('-f', '--fields', default=2, type=int,
                        help='number of fields')
    parser.add_argument('-s', '--step', default=4, type=int,
                        help='number of headers to add in iteration')
    args = parser.parse_args()
    run(args.headers, args.fields, args.step)
