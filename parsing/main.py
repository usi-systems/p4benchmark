#!/usr/bin/env python

import argparse
from bm_parser import benchmark_parser

def main():
    parser = argparse.ArgumentParser(description='A programs that generate a set'
                            ' of P4 programs')
    parser.add_argument('--headers', default=1, type=int, help='number of headers')
    parser.add_argument('--fields', default=1, type=int, help='number of fields')

    args = parser.parse_args()

    benchmark_parser(args.headers, args.fields)

if __name__=='__main__':
    main()