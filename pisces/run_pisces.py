#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from parsing.bm_parser import benchmark_parser_header

dir_path = os.path.dirname(os.path.realpath(__file__))

class P4Benchmark(object):
    def __init__(self, parent_dir, directory, offer_load):
        assert os.environ.get('P4BENCHMARK_ROOT')
        assert os.environ.get('PYTHONPATH')
        assert os.environ.get('OVS_PATH')
        assert os.environ.get('DPDK_BUILD')
        pypath = os.environ.get('PYTHONPATH')
        p4bench = os.environ.get('P4BENCHMARK_ROOT')
        self.ovs = os.environ.get('OVS_PATH')
        self.dpdk = os.environ.get('DPDK_BUILD')
        self.pktgen = os.path.join(p4bench, 'pktgen/build/p4benchmark')
        self.nb_packets = 100000
        self.log_level = ''
        self.parent_dir = parent_dir
        self.directory = directory
        self.offer_load = offer_load


class BenchmarkParser(P4Benchmark):

    def __init__(self, nb_header, offer_load):
        parent_dir = 'result/parse_header'
        directory = '{0}/{1}/{2}'.format(parent_dir, nb_header, offer_load)
        super(BenchmarkParser, self).__init__(parent_dir, directory, offer_load)
        self.nb_header = nb_header
        self.nb_field = 2
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def clean(self):
        cmd = 'make clean'
        p = Popen(shlex.split(cmd))
        p.wait()

    def configure(self):
        ret = benchmark_parser_header(self.nb_header, self.nb_field)
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
        cmd = "make -j4"
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

    def run_remote_pktgen(self):
        cmd = "ssh -t {0} 'sudo {1} -p {2} -s eth1 -i eth2 -c {3} -t {4}' 2> /tmp/pktgen".format('pktgen',
                '/home/vagrant/dpl-benchmark/pktgen/build/p4benchmark',
                '/home/vagrant/dpl-benchmark/pisces/output/test.pcap',
                self.nb_packets,
                self.offer_load)

        print cmd
        args = shlex.split(cmd)
        out_file = '{0}/latency.csv'.format(self.directory)
        out = open(out_file, 'w+')
        p = Popen(args, stdout=out)
        p.wait()
        out.close()
        assert (p.poll() != None)

        cmd = "ssh {0} 'cat /tmp/pktgen'".format('pktgen')
        loss_info = '{0}/loss.csv'.format(self.directory)
        loss_out = open(loss_info, 'w+')
        print cmd
        args = shlex.split(cmd)
        p = Popen(args, stdout=loss_out)
        p.wait()
        loss_out.close()


def run(nb_headers=5, step=5):
    offer_load = 500000
    p = BenchmarkParser(nb_headers, offer_load)
    p.clean()
    p.configure()
    p.make_switch()
    p.run_ovsdb_server()
    p.run_ovs_vswitchd()
    time.sleep(1)
    p.add_flows('vs_commands.txt')
    p.add_flows('commands.txt')
    print "switch is running"
    p.run_remote_pktgen()
    p.stop_ovs_switch('sudo pkill ovsdb-server')
    p.stop_ovs_switch('sudo pkill ovs-vswitchd')

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-n', '--headers', default=5, type=int,
                        help='number of headers from start')
    parser.add_argument('-s', '--step', default=5, type=int,
                        help='number of headers to add in iteration')
    args = parser.parse_args()

    run(args.headers, args.step)
