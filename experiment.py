#!/usr/bin/env python
import argparse
import subprocess
import shlex
import os, sys
from threading import Timer
import time

def gen_p4_parser(host, path, headers, output_dir):
    cmd = "ssh {0} 'mkdir -p temp; cd temp; python {1}/generate_p4_program.py --parser-header --headers {2}'".format(host, path, headers)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd))
    ssh.wait()

def gen_set_field(host, path, fields, output_dir):
    cmd = "ssh {0} 'mkdir -p temp; cd temp; python {1}/generate_p4_program.py --action-complexity --fields {2} --nb-operation {2}'".format(host, path, fields)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd))
    ssh.wait()

def gen_p4_mod_packet(host, path, headers, output_dir):
    cmd = "ssh {0} 'mkdir -p temp; cd temp; python {1}/generate_p4_program.py --mod-packet --mod-type add --headers {2}'".format(host, path, headers)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd))
    ssh.wait()


def compile_p4_program(host, path, output_dir):
    cmd = "ssh {0} 'cd temp; python {1}/pisces/P4vSwitch.py -p ./output/main.p4 -c'".format(host, path)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()

def dump_flows(host):
    cmd = "ssh -t {0} 'sudo temp/utilities/ovs-ofctl --protocols=OpenFlow15 dump-flows br0'".format(host)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()


def run_pisces(host, path, output_dir, rule_file):
    cmd = "ssh {0} 'cd temp; python {1}/pisces/P4vSwitch.py -r {2}'".format(host, path, rule_file)
    print cmd
    with open('%s/switch.txt' % (output_dir), 'w') as out:
        ssh = subprocess.Popen(shlex.split(cmd),
                                stdout=out,
                                stderr=out,
                                shell=False)
    return ssh


def run_moongen(host, path, moongen_path, output_dir, load=1000):
    cmd = "ssh -t {0} 'sudo {1}/build/MoonGen {2}/pktgen/lua_config/pcap_ts_timer.lua 0 1 temp/output/test.pcap -l {3}'".format(host, moongen_path, path, load)
    print cmd
    with open('%s/MoonGen.txt' % (output_dir), 'w') as out:
        ssh = subprocess.Popen(shlex.split(cmd),
                                stdout=out,
                                stderr=out,
                                shell=False)
    return ssh

def copy_histogram(host, moongen_path, output_dir):
    cmd = "scp {0}:{1}/histogram.csv {2}/".format(host, moongen_path, output_dir)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()


def run_my_pktgen(host, path, output_dir, mbps=1000):
    Bps = mbps * (10**6) / 8
    cmd = "ssh -t {0} 'sudo {1}/pktgen/build/p4benchmark -p temp/output/test.pcap -s eth3 -i eth4 -f \"udp and dst port 37009\" -c 10000000 -t {2} 2> /tmp/pktgen'".format(host, path, Bps)
    # cmd = "ssh -t {0} 'sudo {1}/pktgen/build/p4benchmark -p temp/output/test.pcap -s eth3 -i eth4 -f \"udp\" -c 10000000 -t {2} 2> /tmp/pktgen'".format(host, path, Bps)
    print cmd
    with open('%s/latency.csv' % (output_dir), 'w') as out:
        ssh = subprocess.Popen(shlex.split(cmd),
                                stdout=out,
                                shell=False)
        ssh.wait()

    cmd = "ssh {0} 'cat /tmp/pktgen'".format(host)
    with open('%s/loss.csv' % (output_dir), 'w') as loss_file:
        ssh = subprocess.Popen(shlex.split(cmd),
                                stdout=loss_file,
                                shell=False)
        ssh.wait()



def stop_pisces(host, path):
    cmd = "ssh {0} 'python {1}/pisces/P4vSwitch.py -k'".format(host, path)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()


def run_experiment_with_MoonGen(path, moongen_path, variable_path, rule_file):
    load = 1000
    while load <= 10000:
        output_path = '{0}/{1}'.format(variable_path, load)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        switch = run_pisces('node97', path, output_path, rule_file)
        # wait for switch to come up
        time.sleep(5)
        moongen = run_moongen('node98', path, moongen_path, output_path, load)
        moongen.wait()
        copy_histogram('node98', moongen_path, output_path)

        dump_flows('node97')
        stop_pisces('node97', path)
        switch.wait()
        # wait 10s before starting new experiments
        time.sleep(5)
        load += 1000

def run_experiment_with_pktgen(path, variable_path, rule_file):
    load = 500
    output_path = '{0}/{1}'.format(variable_path, load)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    switch = run_pisces('node97', path, output_path, rule_file)
    # wait for switch to come up
    time.sleep(5)
    run_my_pktgen('node98', path, output_path, load)
    dump_flows('node97')
    stop_pisces('node97', path)
    switch.wait()

features = ['parse-field', 'set-field', 'modify']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run P4 benchmark experiment.')
    parser.add_argument('output', help='output directory of the experiment')
    parser.add_argument('--feature', choices=features,
                help='select a feature for benchmarking')
    parser.add_argument('--fields', type=int, default=2,
                help='the number of fields for the benchmarking action-complexity')
    parser.add_argument('--headers', type=int, default=2,
                help='the number of headers for benchmarking packet modification')
    parser.add_argument('--actions', type=int, default=2,
                help='the number of actions for benchmarking parse-field')
    parser.add_argument('--path', default='/home/danghu/workspace/p4benchmark',
                help='path to p4benchmark on the remote server')
    parser.add_argument('--moongen-path', default='/home/danghu/MoonGen',
                help='path to MoonGen on the remote server')
    parser.add_argument('--moongen', default=False, action='store_true',
                help='use p4benchmark packet generator')
    args = parser.parse_args()


    if args.feature == features[0]:
        variable = args.fields
    elif args.feature == features[1]:
        variable = args.actions
    elif args.feature == features[2]:
        variable = args.headers
    else:
        args.print_usages()
        sys.exit(-1)

    # for variable in [1, 2, 4, 8, 16, 32]:
    for variable in [1,]:
        variable_path = '{0}/{1}'.format(args.output, variable)
        if not os.path.exists(variable_path):
           os.makedirs(variable_path)

        if args.feature == features[0]:
            gen_p4_parser('node97', args.path, variable, variable_path)
            gen_p4_parser('node98', args.path, variable, variable_path)
        elif args.feature == features[1]:
            gen_set_field('node97', args.path, variable, variable_path)
            gen_set_field('node98', args.path, variable, variable_path)
        elif args.feature == features[2]:
            gen_p4_mod_packet('node97', args.path, variable, variable_path)
            gen_p4_mod_packet('node98', args.path, variable, variable_path)

        compile_p4_program('node97', args.path, variable_path)

        if args.moongen:
            run_experiment_with_MoonGen(args.path, args.moongen_path, variable_path, '~/temp/output/pisces_rules.txt')
        else:
            if args.feature == features[0]:
                run_experiment_with_pktgen(args.path, variable_path, args.path + 'pisces/commands.txt')
            elif args.feature == features[1]:
                run_experiment_with_pktgen(args.path, variable_path, '~/temp/output/pisces_rules.txt')
            elif args.feature == features[2]:
                run_experiment_with_pktgen(args.path, variable_path, '~/temp/output/pisces_rules.txt')
