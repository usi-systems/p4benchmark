#!/usr/bin/env python

import argparse
from bm_memory import benchmark_memory

def main():
    parser = argparse.ArgumentParser(description='A programs that generate a set'
                            ' of P4 programs')
    parser.add_argument('--register', default=1, type=int, help='number of registers')
    parser.add_argument('--width', default=32, type=int,
                            help='the bit width of a register element')
    parser.add_argument('--element', default=1024, type=int,
                            help='number of element in a register')
    parser.add_argument('--operation', default=1, type=int,
                            help='number of register operation')

    args = parser.parse_args()
    benchmark_memory(args.register, args.width, args.element, args.operation)

if __name__=='__main__':
    main()