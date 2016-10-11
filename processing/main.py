#!/usr/bin/env python

import argparse
from bm_pipeline import benchmark_pipeline

def main():
    parser = argparse.ArgumentParser(description='A programs that generate a set'
                            ' of P4 programs')
    parser.add_argument('--table', default=1, type=int, help='number of tables')
    parser.add_argument('--size', default=1, type=int,
                            help='number of rows in the table')

    args = parser.parse_args()
    benchmark_pipeline(args.table, args.size)

if __name__=='__main__':
    main()