#!/usr/bin/env python

import os
import json
import argparse
import multiprocessing
import sys
import numpy as np


def load_tsv(path):
    rows = []
    with open(path, 'r') as f:
        for line in f.readlines():
            rows.append(map(float, line.split()))
    return rows


def parse_experiment(exp_dir):
    assert os.path.isdir(exp_dir)
    json_path = os.path.join(exp_dir, 'experiment.json')
    assert os.path.isfile(json_path)

    out_path = os.path.join(exp_dir, 'out')
    assert os.path.isdir(out_path)
    results_path = os.path.join(out_path, 'results.tsv')
    assert os.path.isfile(results_path)
    stats_path = os.path.join(out_path, 'load_stats.tsv')
    assert os.path.isfile(stats_path)

    with open(json_path, 'r') as f:
        conf = json.load(f)
        assert type(conf) is dict

    exp = dict(conf.items())

    load_stats = load_tsv(stats_path)
    assert len(load_stats) == 1 and len(load_stats[0]) == 4
    exp['sent'], exp['recv'], exp['lost'], exp['tput'] = load_stats[0]

    results = load_tsv(results_path)
    cols = zip(*results)
    exp['avg_latency'] = np.mean(cols[0])
    exp['min_latency'] = np.min(cols[0])
    exp['max_latency'] = np.max(cols[0])
    exp['p99_latency'] = np.percentile(cols[0], 99)
    exp['p95_latency'] = np.percentile(cols[0], 95)
    exp['std_latency'] = np.std(cols[0])
    exp['cv_latency'] = exp['std_latency'] / exp['avg_latency']

    return exp


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=str, help="experiment directory", nargs='*')
    parser.add_argument("--jobs", "-j", type=int, action="store", default=None, help="number of parallel jobs")
    parser.add_argument("--json", "-J", action="store_true", help="output as JSON")
    parser.add_argument("--header", "-H", action="store_true", help="print header")
    args = parser.parse_args()

    n_job = args.jobs
    if n_job is None:
        n_cpu = multiprocessing.cpu_count()
        n_job = n_cpu if n_cpu == 1 else n_cpu - 1

    if n_job > 1:
        p = multiprocessing.Pool(n_job)
        experiments = p.map(parse_experiment, args.dir)
    else:
        experiments = map(parse_experiment, args.dir)

    if args.json:
        print json.dumps(experiments, indent=1, sort_keys=True)
    else:
        keys = sorted(experiments[0].keys())
        if args.header:
            print '\t'.join(keys)
        print '\n'.join(['\t'.join([str(s[k] if k in s else 0) for k in keys]) for s in experiments])
