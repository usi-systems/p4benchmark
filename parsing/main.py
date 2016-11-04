#!/usr/bin/env python

import argparse

from parsing.bm_parser import benchmark_parser_header
from parsing.bm_parser import benchmark_parser_with_header_field
from parsing.bm_parser import parser_complexity


features = ['parse-header', 'parse-field', 'parse-complex' ]

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
    # Parser Complexity
    parser.add_argument('--depth', default=1, type=int,
                            help='the depth of the parse graph')
    parser.add_argument('--fanout', default=2, type=int,
                            help='the number of branch of a node in the parse graph')

    args = parser.parse_args()

    if args.feature == 'parse-header':
        benchmark_parser_header(args.headers, args.fields, do_checksum=args.checksum)
    elif args.feature == 'parse-field':
        benchmark_parser_with_header_field(args.fields, do_checksum=args.checksum)
    elif args.feature == 'parse-complex':
        parser_complexity(args.depth, args.fanout)

if __name__=='__main__':
    main()
