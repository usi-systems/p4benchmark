#!/usr/bin/env python

import argparse

from bm_modification import benchmark_modification


features = [
            'add-header', 'rm-header',                      # Packet Modification
            ]

def main():
    parser = argparse.ArgumentParser(description='A programs that generate a'
                            ' P4 program for benchmarking a particular feature')
    parser.add_argument('--feature', choices=features,
                help='select a feature for benchmarking')
    parser.add_argument('--checksum', default=False, action='store_true',
                            help='perform update checksum')
    # Parser (Field|Header) and Packet Modification options
    parser.add_argument('--headers', default=1, type=int, help='number of headers')
    parser.add_argument('--fields', default=1, type=int, help='number of fields')

    args = parser.parse_args()

    if args.feature == 'add-header':
        benchmark_modification(args.headers, args.fields, 'add')
    elif args.feature == 'rm-header':
        benchmark_modification(args.headers, args.fields, 'rm')

if __name__=='__main__':
    main()
