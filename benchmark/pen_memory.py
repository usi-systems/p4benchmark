#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from state_access.bm_memory import benchmark_memory
from benchmark import P4Benchmark

class BenchmarkMemory(P4Benchmark):

    def __init__(self, nb_registers, element_size, nb_elements, offer_load):
        parent_dir = 'result/registers'
        directory = '{0}/s-{1}/{2}/{3}'.format(parent_dir,
                        element_size, nb_registers, offer_load)
        super(BenchmarkMemory, self).__init__(parent_dir, directory, offer_load)
        self.nb_registers = nb_registers
        self.element_size = element_size
        self.nb_elements = nb_elements
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)


    def compile_p4_program(self):
        ret = benchmark_memory(self.nb_registers, self.element_size, self.nb_elements, 1)
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
    parser.add_argument('-n', '--nb-registers', default=5, type=int,
                        help='number of registers from start')
    parser.add_argument('-e', '--element-size', default=32, type=int,
                        help='element size')
    parser.add_argument('-l', '--nb-elements', default=32, type=int,
                        help='nb_elements')
    args = parser.parse_args()

    nb_registers = args.nb_registers

    while(nb_registers <= 40):
        offer_load = 100000
        p = BenchmarkMemory(nb_registers, args.element_size, args.nb_elements, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = BenchmarkMemory(nb_registers, args.element_size, args.nb_elements, offer_load)
            p.start()

        nb_registers += 5

    p.run_analyser()

if __name__=='__main__':
    main()
