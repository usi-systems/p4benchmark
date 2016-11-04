#!/usr/bin/env python

import argparse

from bm_memory import benchmark_memory

features = ['read-state', 'write-state']

def main():
    parser = argparse.ArgumentParser(description='A programs that generate a'
                            ' P4 program for benchmarking a particular feature')
    parser.add_argument('--feature', choices=features,
                help='select a feature for benchmarking')
    parser.add_argument('--checksum', default=False, action='store_true',
                            help='perform update checksum')
    # State Access option
    parser.add_argument('--registers', default=1, type=int, help='number of registers')
    parser.add_argument('--nb-element', default=1024, type=int,
                            help='number of element in a register')
    parser.add_argument('--element-width', default=32, type=int,
                            help='the bit width of a register element')
    parser.add_argument('--operations', default=1, type=int,
                            help='the number of set-field/read/write operations')

    args = parser.parse_args()

    if args.feature == 'read-state':
        benchmark_memory(args.registers, args.element_width, args.nb_element,
                            args.operations, False)
    elif args.feature == 'write-state':
        benchmark_memory(args.registers, args.element_width, args.nb_element,
                            args.operations, True)

if __name__=='__main__':
    main()
