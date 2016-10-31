#!/usr/bin/env python

import os
import json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load Experiment Generator')
    parser.add_argument('-o', '--out-dir', help='path to parent directory to save experiment in',
            type=str, required=True)
    parser.add_argument("--param", "-p", help='Set parameters. E.g.: -p load=1000 -p count=10000', action='append',
        type=lambda kv: kv.split("="), dest='parameters')
    args = parser.parse_args()

    exp_name = '_'.join(['%s_%s' % (p[1], p[0]) for p in args.parameters])
    exp_dir_path = os.path.join(args.out_dir, exp_name)
    os.mkdir(exp_dir_path)

    exp_json_path = os.path.join(exp_dir_path, 'experiment.json')

    conf = dict(args.parameters)

    with open(exp_json_path, 'w') as f:
        json.dump(conf, f, indent=4)

    print exp_json_path
