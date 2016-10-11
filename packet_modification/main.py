#!/usr/bin/env python

import argparse
from bm_modification import benchmark_modification

def main():
    parser = argparse.ArgumentParser(description='A programs that generate a set'
                            ' of P4 programs')
    parser.add_argument('--headers', default=1, type=int, help='number of headers')
    parser.add_argument('--fields', default=1, type=int, help='number of fields')
    parser.add_argument('--mod-type', default='add', type=str,
                            help='modification type [add, rm, mod]')

    args = parser.parse_args()
    benchmark_modification(args.headers, args.fields, args.mod_type)

if __name__=='__main__':
    main()