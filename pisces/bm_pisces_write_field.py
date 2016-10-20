#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from parsing.bm_parser import benchmark_parser_header
from action_complexity.bm_mod_field import benchmark_field_write

dir_path = os.path.dirname(os.path.realpath(__file__))

class P4Benchmark(object):
    def __init__(self, parent_dir, directory, offer_load):
        assert os.environ.get('P4BENCHMARK_ROOT')
        assert os.environ.get('PYTHONPATH')
        assert os.environ.get('OVS_PATH')
        pypath = os.environ.get('PYTHONPATH')
        p4bench = os.environ.get('P4BENCHMARK_ROOT')
        self.ovs = os.environ.get('OVS_PATH')
	print 'OVS_PATH', self.ovs
        self.dpdk = os.environ.get('DPDK_BUILD')
	print 'DPDK_BUILD', self.dpdk
        bmv2 = os.path.join(p4bench, 'behavioral-model')
        self.p4c = os.path.join(p4bench, 'p4c-bm/p4c_bm/__main__.py')
        self.switch_path = os.path.join(bmv2, 'targets/simple_switch/simple_switch')
        self.cli_path = os.path.join(bmv2, 'tools/runtime_CLI.py')
        self.pktgen = os.path.join(p4bench, 'pktgen/build/p4benchmark')
        self.analyse = os.path.join(p4bench, 'benchmark/analyse.R')
        self.nb_packets = 1000000
        self.log_level = ''
        self.parent_dir = parent_dir
        self.directory = directory
        self.offer_load = offer_load

class BenchmarkPisces(P4Benchmark):

    def __init__(self, nb_field, offer_load):
        parent_dir = 'result/'
        directory = '{0}/{1}/{2}'.format(parent_dir, nb_field, offer_load)
        super(BenchmarkPisces, self).__init__(parent_dir, directory, offer_load)
        self.nb_field = nb_field
        self.nb_header = 1
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def clean(self):
        cmd = 'make clean'
        p = Popen(shlex.split(cmd))
        p.wait()

    def configure(self):
        ret = benchmark_field_write(self.nb_header, self.nb_field)
        assert (ret == True)
        prog = 'main'
        cmd =   """{0}/configure --with-dpdk={1}
                CFLAGS="-g -O2 -Wno-cast-align"
                p4inputfile={2}
                p4outputdir={3}/include/p4/src""".format(
                self.ovs, self.dpdk, 'output/main.p4', dir_path)
        print cmd
        out_file = '{0}/pisces_compiler.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen(shlex.split(cmd), stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)

    def make_switch(self):
        cmd = "make -j8"
        print cmd
        out_file = '{0}/pisces_make.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen(shlex.split(cmd), stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)

    def run_ovsdb_server(self):
        cmd = """sudo ./ovsdb/ovsdb-server
                --remote=punix:/usr/local/var/run/openvswitch/db.sock
                --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile"""
        print cmd
        out_file = '{0}/ovsdb_server.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            self.ovsdb_server = Popen(shlex.split(cmd), stdout=out, stderr=out)

    def run_ovs_vswitchd(self):
        cmd = """sudo ./vswitchd/ovs-vswitchd --dpdk -c 0x1 -n 4
                -- unix:/usr/local/var/run/openvswitch/db.sock --pidfile"""
        print cmd
        out_file = '{0}/ovs_vswitchd.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            self.ovs_vswitchd = Popen(shlex.split(cmd), stdout=out, stderr=out)

    def add_flows(self, command_file):
        with open(command_file, 'r') as fin:
            for line in fin:
                cmd = """sudo {0}/{1}""".format('utilities', line)
                print cmd
                p = Popen(shlex.split(cmd))
                p.wait()

    def stop_ovs_switch(self, cmd):
        args = shlex.split(cmd)
        p = Popen(args)
        out, err = p.communicate()
        if out:
            print out
        if err:
            print err
        self.ovsdb_server.wait()
        assert (self.ovsdb_server.poll() != None)
        time.sleep(5)


def run(nb_fields=4, step=4):
    offer_load = 1000
    p = BenchmarkPisces(nb_fields, offer_load)
    p.clean()
    p.configure()
    p.make_switch()
    p.run_ovsdb_server()
    p.run_ovs_vswitchd()
    time.sleep(1)
    p.add_flows('vs_commands.txt')
    p.add_flows('commands.txt')
    print "switch is running"
    time.sleep(2)
    p.stop_ovs_switch('sudo pkill ovsdb-server')
    p.stop_ovs_switch('sudo pkill ovs-vswitchd')

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-n', '--fields', default=4, type=int,
                        help='number of fields')
    parser.add_argument('-s', '--step', default=4, type=int,
                        help='number of fields to add in iteration')
    args = parser.parse_args()

    run(args.fields, args.step)
