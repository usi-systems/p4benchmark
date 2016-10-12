#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from state_access.bm_memory import benchmark_memory
from benchmark.benchmark import P4Benchmark

class RegisterBenchmark(P4Benchmark):

    def __init__(self, operation, offer_load):
        parent_dir = 'result/read_different_register'
        directory = '{0}/{1}/{2}'.format(parent_dir, operation, offer_load)
        super(RegisterBenchmark, self).__init__(parent_dir, directory, offer_load)
        self.operation = operation
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def compile_p4_program(self):
        # each operation read from a distinguished register
        registers = self.operation
        ret = benchmark_memory(registers, 32, 1024, 1, False)
        assert (ret == True)
        prog = 'main'
        json_path = 'output/%s.json' % prog
        out_file = '{0}/p4c.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen([self.p4c, 'output/%s.p4' % prog , '--json', json_path],
                stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)

def run(operation=5):
    while(operation <= 40):
        offer_load = 100000
        p = RegisterBenchmark(operation, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = RegisterBenchmark(operation, offer_load)
            p.start()
        operation += 5

    p.run_analyser()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-n', '--operation', default=5, type=int,
                        help='number of operations')
    args = parser.parse_args()
    run(args.operations)
