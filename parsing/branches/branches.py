#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from parsing.bm_parser import parser_complexity
from benchmark.benchmark import P4Benchmark

class ComplexityDepth(P4Benchmark):

    def __init__(self, aspect, depth, fanout, offer_load):
        parent_dir = 'result/%s' % aspect
        directory = '{0}/{1}/{2}'.format(parent_dir, depth, offer_load)
        super(ComplexityDepth, self).__init__(parent_dir, directory, offer_load)
        self.depth = depth
        self.fanout = fanout
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def compile_p4_program(self):
        ret = parser_complexity(self.depth, self.fanout)
        assert (ret == True)
        prog = 'main'
        json_path = 'output/%s.json' % prog
        out_file = '{0}/p4c.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen([self.p4c, 'output/%s.p4' % prog , '--json', json_path],
                stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)

def vary_depth(depth=2, fanout=2):
    while(depth <= 10):
        offer_load = 100000
        p = ComplexityDepth('depth', depth, fanout, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = ComplexityDepth('depth', depth, fanout, offer_load)
            p.start()
        depth += 1
    p.run_analyser()

def vary_fanout(fanout=2, depth=2):
    while(fanout <= 10):
        offer_load = 100000
        p = ComplexityDepth('fanout', depth, fanout, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = ComplexityDepth('depth', depth, fanout, offer_load)
            p.start()
        fanout += 1
    p.run_analyser()

def run(depth=2, fanout=2):
    vary_depth(depth, fanout)
    vary_fanout(fanout, depth)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-d', '--depth', default=1, type=int,
                        help='the height of parsing tree')
    parser.add_argument('-f', '--fanout', default=2, type=int,
                        help='the number of children of a node')
    args = parser.parse_args()
    depth = args.depth
    fanout = args.fanout
    run(depth, fanout)
