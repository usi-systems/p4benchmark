#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from processing.bm_pipeline import benchmark_pipeline
from benchmark.benchmark import P4Benchmark

class BenchmarkProcessingTable(P4Benchmark):

    def __init__(self, nb_table, tbl_size, offer_load):
        self.nb_table = nb_table
        self.tbl_size = tbl_size
        parent_dir = 'result/processing'
        directory = '{0}/size-{1}/{2}/{3}'.format(parent_dir, self.tbl_size,
                            self.nb_table, offer_load)
        super(BenchmarkProcessingTable, self).__init__(parent_dir, directory, offer_load)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def compile_p4_program(self):
        ret = benchmark_pipeline(self.nb_table, self.tbl_size)
        assert (ret == True)
        prog = 'main'
        json_path = 'output/%s.json' % prog
        out_file = '{0}/p4c.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen([self.p4c, 'output/%s.p4' % prog , '--json', json_path],
                stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)


def run(nb_table=5, tbl_size=32):
    while(nb_table <= 40):
        offer_load = 100000
        p = BenchmarkProcessingTable(nb_table, tbl_size, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = BenchmarkProcessingTable(nb_table, tbl_size, offer_load)
            p.start()
        nb_table += 5
    p.run_analyser()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-n', '--table', default=5, type=int,
                        help='number of tables from start')
    parser.add_argument('-s', '--size', default=32, type=int,
                        help='table size')
    args = parser.parse_args()
    run(args.nb_table, tbl_size)
