#!/usr/bin/env python
import argparse
import subprocess
import shlex
import os
from threading import Timer
import time


def gen_p4_program(host, path, fields, output_dir):
    cmd = "ssh {0} 'mkdir -p temp; cd temp; python {1}/generate_p4_program.py --action-complexity --fields {2}'".format(host, path, fields)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd))
    ssh.wait()


def compile_p4_program(host, path, output_dir):
    cmd = "ssh {0} 'cd temp; python {1}/pisces/P4vSwitch.py -p ./output/main.p4 -c'".format(host, path)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()


def run_pisces(host, path, output_dir):
    cmd = "ssh {0} 'cd temp; python {1}/pisces/P4vSwitch.py -r {1}/pisces/write_fields.txt'".format(host, path)
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


def stop_pisces(host, path):
    cmd = "ssh {0} 'python {1}/pisces/P4vSwitch.py -k'".format(host, path)
    print cmd
    ssh = subprocess.Popen(shlex.split(cmd), shell=False)
    ssh.wait()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run P4 benchmark experiment.')
    parser.add_argument('output', help='output directory of the experiment')
    parser.add_argument('--fields', type=int, default=2,
                help='the number of fields for the benchmark action-complexity')
    parser.add_argument('--path', default='/home/danghu/workspace/p4benchmark',
                help='path to p4benchmark on the remote server')
    parser.add_argument('--moongen', default='/home/danghu/MoonGen',
                help='path to MoonGen on the remote server')
    args = parser.parse_args()

    try:

        while args.fields <= 20:
            variable_path = '{0}/{1}'.format(args.output, args.fields)
            if not os.path.exists(variable_path):
               os.makedirs(variable_path)

            gen_p4_program('node97', args.path, args.fields, variable_path)
            gen_p4_program('node98', args.path, args.fields, variable_path)
            compile_p4_program('node97', args.path, variable_path)

            load = 10000
            while load <= 10000:
                output_path = '{0}/{1}'.format(variable_path, load)
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                switch = run_pisces('node97', args.path, output_path)
                # wait for switch to come up
                time.sleep(5)
                moongen = run_moongen('node98', args.path, args.moongen, output_path, load)
                moongen.wait()
                copy_histogram('node98', args.moongen, output_path)

                stop_pisces('node97', args.path)
                switch.wait()
                # wait 10s before starting new experiments
                time.sleep(5)
                load += 1000
            args.fields += 2

    finally:
        pass