#!/usr/bin/env python

import os
import argparse
from subprocess import call, Popen, PIPE
import shlex
import time
from packet_modification.bm_modification import benchmark_modification
from benchmark import P4Benchmark

class BenchmarkPacketMod(P4Benchmark):

    def __init__(self, nb_operations, nb_fields, offer_load):
        parent_dir = 'result/packetMod'
        directory = '{0}/fields-{1}/{2}/{3}'.format(parent_dir,
                        nb_fields, nb_operations, offer_load)
        super(BenchmarkPacketMod, self).__init__(parent_dir, directory, offer_load)
        self.nb_operations = nb_operations
        self.nb_fields = nb_fields
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)


    def compile_p4_program(self):
        ret = benchmark_modification(self.nb_operations, self.nb_fields, 'mod')
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
    parser.add_argument('-n', '--nb-operations', default=5, type=int,
                        help='number of operations from start')
    parser.add_argument('-f', '--nb-fields', default=2, type=int,
                        help='number of fields for each header')
    args = parser.parse_args()

    nb_operations = args.nb_operations

    while(nb_operations <= 40):
        offer_load = 100000
        p = BenchmarkPacketMod(nb_operations, args.nb_fields, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = BenchmarkPacketMod(nb_operations, args.nb_fields, offer_load)
            p.start()

        nb_operations += 5
    p.run_analyser()

if __name__=='__main__':
    main()
