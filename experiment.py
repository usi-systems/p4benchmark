#!/usr/bin/env python
import argparse
import subprocess
import shlex
import os, sys
import time


features = ['parse-header', 'parse-field', 'set-field', 'modify', 'processing']

def copy_p4_program(host, input_program):
    cmd = "scp {0} {1}:temp/output/main.p4".format(input_program, host)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd))
    ssh.wait()

def gen_p4_program(host, feature, path, variable, output_dir, checksum, num_fields=4):
    cmd  = "ssh {0} 'mkdir -p temp; cd temp;".format(host)
    if checksum:
        cmd += " python {0}/generate_p4_program.py --checksum".format(path)
    else:
        cmd += " python {0}/generate_p4_program.py".format(path)
    if feature == features[0]:
        cmd += " --parser-header --headers {0} --fields {1}'".format(variable, num_fields)
    if feature == features[1]:
        cmd += " --parser-field --fields {0}'".format(variable)
    elif feature == features[2]:
        cmd += " --action-complexity --nb-operation {0}'".format(variable)
    elif feature == features[3]:
        cmd += " --mod-packet --mod-type add --headers {0}'".format(variable)
    elif feature == features[4]:
        cmd += " --pipeline --tables {0}'".format(variable)
    else:
        print "{0} is not a valid benchmarking feature".format(feature)
        sys.exit(1)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd))
    ssh.wait()


def compile_p4_program(host, path, output_dir):
    cmd = "ssh {0} 'cd temp; python {1}/pisces/P4vSwitch.py -p ./output/main.p4 -c'".format(host, path)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()

def dump_flows(host, output_dir):
    cmd = "ssh -t {0} 'sudo temp/utilities/ovs-ofctl --protocols=OpenFlow15 dump-flows br0'".format(host)
    print cmd
    with open('%s/dump_flows.txt' % (output_dir), 'w') as out:
        ssh = subprocess.Popen(shlex.split(cmd),
                                stdout=out,
                                stderr=out,
                                shell=False)
    ssh.wait()

def dump_ports(host, output_dir):
    cmd = "ssh -t {0} 'sudo temp/utilities/ovs-ofctl --protocols=OpenFlow15 dump-ports br0'".format(host)
    print cmd
    with open('%s/dump_ports.txt' % (output_dir), 'w') as out:
        ssh = subprocess.Popen(shlex.split(cmd),
                                stdout=out,
                                stderr=out,
                                shell=False)
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


def run_moongen(host, path, moongen_path, output_dir, metric, variable, rate=1000, num_fields=4):
    if metric == 'throughput':
        cmd = "ssh -t {0} 'sudo {1}/build/MoonGen {2}/pktgen/lua_config/hardware-timestamping.lua 0 1 -f temp/output/test.pcap --rate {3} -n {4} -s {5}'".format(host, moongen_path, path, rate, variable, num_fields*2)
    else:
        cmd = "ssh -t {0} 'sudo {1}/build/MoonGen {2}/pktgen/lua_config/hardware-timestamping.lua 0 1 --rate {3} -n {4} -s {5}'".format(host, moongen_path, path, rate, variable, num_fields*2)
    print cmd
    with open('%s/MoonGen.txt' % (output_dir), 'w') as out:
        ssh = subprocess.Popen(shlex.split(cmd),
                                stdout=out,
                                stderr=out,
                                shell=False)
    return ssh


def copy_histogram(host, moongen_path, output_dir):
    cmd = "scp {0}:histogram.csv {2}/".format(host, moongen_path, output_dir)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()

def rm_histogram(host):
    cmd = "ssh {0} 'rm histogram.csv'".format(host)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()


def stop_pisces(host, path):
    cmd = "ssh {0} 'python {1}/pisces/P4vSwitch.py -k'".format(host, path)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()

def run_N_experiments(path, moongen_path, variable_path, metric, variable, N=1):
    i = 0
    while i < N:
        # line rate
        rate = 10000
        output_path = '{0}/{1}/{2}'.format(variable_path, i, rate)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        switch = run_pisces('node97', path, output_path, '~/temp/output/pisces_rules.txt')
        # wait for switch to come up
        time.sleep(5)
        moongen = run_moongen('node98', path, moongen_path, output_path, metric, variable, rate)
        moongen.wait()
        copy_histogram('node98', moongen_path, output_path)
        rm_histogram('node98')

        dump_flows('node97', output_path)
        stop_pisces('node97', path)
        switch.wait()
        # wait 10s before starting new experiments
        time.sleep(5)
        i += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run P4 benchmark experiment.')
    parser.add_argument('output', help='output directory of the experiment')
    parser.add_argument('--feature', choices=features,
                help='select a feature for benchmarking')
    parser.add_argument('--measure', choices=['latency', 'throughput'], default='latency',
                help='choices for measuring metric')
    parser.add_argument('--path', default='/home/danghu/workspace/p4benchmark',
                help='path to p4benchmark on the remote server')
    parser.add_argument('--moongen-path', default='/home/danghu/MoonGen',
                help='path to MoonGen on the remote server')
    parser.add_argument('--checksum', default=False, action='store_true',
                            help='perform update checksum')
    args = parser.parse_args()


    for variable in [1, 2, 4, 8, 16]:
        variable_path = '{0}/{1}'.format(args.output, variable)
        if not os.path.exists(variable_path):
           os.makedirs(variable_path)

        gen_p4_program('node97', args.feature, args.path, variable, variable_path, args.checksum)
        gen_p4_program('node98', args.feature, args.path, variable, variable_path, args.checksum)

        compile_p4_program('node97', args.path, variable_path)
        run_N_experiments(args.path, args.moongen_path, variable_path, args.measure, variable, 5)
