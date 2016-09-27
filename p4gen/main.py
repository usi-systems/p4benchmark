#!/usr/bin/env python

import argparse

from bm_pipeline import *
from bm_parser import *
from bm_memory import *

def main():
    parser = argparse.ArgumentParser(description='A programs that generate a set'
                            ' of P4 programs')
    parser.add_argument('-p', '--parser', default=False, action='store_true',
                            help='parser benchmark')
    parser.add_argument('--pipeline', default=False, action='store_true',
                            help='pipeline benchmark')
    parser.add_argument('--memory', default=False, action='store_true',
                            help='memory consumption benchmark')
    parser.add_argument('--tables', default=1, type=int, help='number of tables')
    parser.add_argument('--table-size', default=1, type=int,
                            help='number of rules in the table')
    parser.add_argument('--headers', default=1, type=int, help='number of headers')
    parser.add_argument('--fields', default=1, type=int, help='number of fields')
    parser.add_argument('--registers', default=1, type=int, help='number of registers')
    parser.add_argument('--nb-element', default=1024, type=int,
                            help='number of element in a register')
    parser.add_argument('--element-width', default=32, type=int,
                            help='the bit width of a register element')

    args = parser.parse_args()

    if args.parser:
        benchmark_parser(args)
    elif args.pipeline:
        benchmark_pipeline(args)
    elif args.memory:
        benchmark_memory(args)
    else:
        parser.print_help()

if __name__=='__main__':
    main()