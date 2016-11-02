#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import time
import json
import argparse
from switch import BMV2Switch
from load_gen import SendB2B

assert os.environ.get('P4BENCHMARK_ROOT')
assert os.environ.get('PYTHONPATH')
P4BENCHMARK_ROOT = os.environ.get('P4BENCHMARK_ROOT')
P4C = os.path.join(P4BENCHMARK_ROOT, 'p4c-bm/p4c_bm/__main__.py')

from packet_modification.bm_modification import benchmark_modification
from state_access.bm_memory import benchmark_memory
from action_complexity.bm_mod_field import benchmark_field_write
from processing.bm_pipeline import benchmark_pipeline
from parsing.bm_parser import benchmark_parser_header

def run_with_load(load=None, count=100000):
    sw = BMV2Switch(json_path='output/main.json', commands_path='output/commands.txt')
    sender = SendB2B(pcap_path='output/test.pcap', count=count)

    sw.start()
    time.sleep(1)
    sender.run()
    sw.kill()

    sent, recv, lost, tput, duration = sender.send_stats()
    return (sent, recv, lost, tput, duration, sender.results())

def clean_results(results):
    if len(results) < 4: return results
    return results[2:-1]

def build_p4_prog():
    prog = 'main'
    with open('p4c.log', 'w+') as out:
        p = Popen([P4C, 'output/%s.p4' % prog , '--json', 'output/%s.json' % prog],
            stdout=out, stderr=out)
        p.wait()
        assert p.returncode == 0

def dump_tsv(l, out_path):
    out = '\n'.join(map(lambda r: '\t'.join(map(lambda x: '%g'%x, r)), l))
    with open(out_path, 'w') as f:
        f.write(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load Experiment Runner')
    parser.add_argument('json_file', help='path to json file describing experiment', type=str)
    args = parser.parse_args()

    # Load the conf for this experiment
    assert os.path.isfile(args.json_file)
    with open(args.json_file, 'r') as f:
        conf = json.load(f)
        assert type(conf) is dict

    # Create the directory we will run in
    exp_dir_path = os.path.dirname(args.json_file)
    exp_out_path = os.path.join(exp_dir_path, 'out')
    if os.path.exists(exp_out_path):
        assert os.path.isdir(exp_out_path)
    else:
        os.mkdir(exp_out_path)
    os.chdir(exp_out_path)

    assert 'type' in conf

    # Generate the P4 program, test pcap, etc.
    if conf['type'] == 'mod':
        assert 'operations' in conf
        assert 'fields' in conf
        ret = benchmark_modification(int(conf['operations']), int(conf['fields']), 'mod')
        assert ret == True
        build_p4_prog()
    elif conf['type'] == 'field':
        assert 'operations' in conf
        ret = benchmark_field_write(int(conf['operations']))
        assert ret == True
        build_p4_prog()
    elif conf['type'] == 'mem':
        assert 'registers' in conf and 'size' in conf and 'elements' in conf and 'operations' in conf
        ret = benchmark_memory(int(conf['registers']), int(conf['size']), int(conf['elements']), int(conf['operations']), True)
        assert ret == True
        build_p4_prog()
    elif conf['type'] == 'pipeline':
        assert 'tables' in conf and 'tbl_size' in conf
        ret = benchmark_pipeline(int(conf['tables']), int(conf['tbl_size']))
        assert ret == True
        build_p4_prog()
    elif conf['type'] == 'parser':
        assert 'headers' in conf and 'fields' in conf
        ret = benchmark_parser_header(int(conf['headers']), int(conf['fields']))
        assert ret == True
        build_p4_prog()
    else:
        assert False, "unknown experiment type: " + conf['type']

    count = int(conf['count']) if 'count' in conf else 100000

    # Run the experiment with the switch and load generator
    sent, recv, lost, tput, duration, results = run_with_load(count=count)

    # Save the results
    dump_tsv(clean_results(results), 'results.tsv')
    dump_tsv([[sent, recv, lost, tput, duration]], 'load_stats.tsv')
