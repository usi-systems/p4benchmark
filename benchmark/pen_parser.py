#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from parsing.bm_parser import benchmark_parser_header

from benchmark import P4Benchmark

class BenchmarkParser(P4Benchmark):

    def __init__(self, nb_header, offer_load):
        parent_dir = 'result/parser/'
        directory = '{0}/{1}/{2}'.format(parent_dir, nb_header, offer_load)
        super(BenchmarkParser, self).__init__(parent_dir, directory, offer_load)
        self.nb_header = nb_header
        self.nb_field = 1
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def compile_p4_program(self):
        ret = benchmark_parser_header(self.nb_header, self.nb_field)
        assert (ret == True)
        prog = 'main'
        json_path = 'output/%s.json' % prog
        out_file = '{0}/p4c.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen([self.p4c, 'output/%s.p4' % prog , '--json', json_path],
                stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)


def main():
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-n', '--nb-headers', default=5, type=int,
                        help='number of headers from start')
    args = parser.parse_args()

    nb_headers = args.nb_headers

    while(nb_headers <= 40):
        offer_load = 100000
        p = BenchmarkParser(nb_headers, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = BenchmarkParser(nb_headers, offer_load)
            p.start()

        nb_headers += 5
    p.run_analyser()

if __name__=='__main__':
    main()
