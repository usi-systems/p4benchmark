#!/usr/bin/env python

import argparse

from bm_mod_field import benchmark_field_write

def main():
    parser = argparse.ArgumentParser(description='A programs that generate a'
                            ' P4 program for benchmarking a particular feature')
    parser.add_argument('--checksum', default=False, action='store_true',
                            help='perform update checksum')
    # Parser Action complexity
    parser.add_argument('--operations', default=1, type=int,
                            help='the number of set-field operations')
    args = parser.parse_args()
    benchmark_field_write(args.operations, do_checksum=args.checksum)

if __name__=='__main__':
    main()
