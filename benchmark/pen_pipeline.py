#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
from processing.bm_pipeline import benchmark_pipeline
from benchmark import P4Benchmark

class BenchmarkPipelineDepth(P4Benchmark):

    def __init__(self, nb_tables, tbl_size, offer_load):
        self.nb_tables = nb_tables
        self.tbl_size = tbl_size
        parent_dir = 'result/pipeline'
        directory = '{0}/size-{1}/{2}/{3}'.format(parent_dir, self.tbl_size,
                            self.nb_tables, offer_load)
        super(BenchmarkPipelineDepth, self).__init__(parent_dir, directory, offer_load)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def tearDown(self):
        cmd = 'sudo pkill lt-simple_swi'
        args = shlex.split(cmd)
        p = Popen(args)
        out, err = p.communicate()
        if out:
            print out
        if err:
            print err
        self.p.wait()
        assert (self.p.poll() != None)
        time.sleep(5)

    def add_rules(self, json_path, commands, retries):
        if retries > 0:
            cmd = [self.cli_path, '--json', json_path]
            if os.path.isfile(commands):
                with open(commands, "r") as f:
                    p = Popen(cmd, stdin=f, stdout=PIPE, stderr=PIPE)
                    out, err = p.communicate()
                    if out:
                        print out
                        if "Could not" in out:
                            print "Retry in 1 second"
                            time.sleep(1)
                            return self.add_rules(json_path, port_number, commands, retries-1)
                        elif  "DUPLICATE_ENTRY" in out:
                            pass
                    if err:
                        print err
                        time.sleep(1)
                        return self.add_rules(json_path, port_number, commands, retries-1)

    def run_packet_generator(self):
        cmd = 'sudo {0} -p {1} -i veth4 -c {2} -t {3}'.format(self.pktgen,
            'output/test.pcap', self.nb_packets, self.offer_load)
        print cmd
        args = shlex.split(cmd)
        out_file = '{0}/latency.csv'.format(self.directory)
        err_file = '{0}/loss.csv'.format(self.directory)
        out = open(out_file, 'w+')
        err = open(err_file, 'w+')
        p = Popen(args, stdout=out, stderr=err)
        p.wait()
        out.close()
        err.close()

    def compile_p4_program(self):
        ret = benchmark_pipeline(self.nb_tables, self.tbl_size)
        assert (ret == True)
        prog = 'main'
        json_path = 'output/%s.json' % prog
        out_file = '{0}/p4c.log'.format(self.directory)
        with open(out_file, 'w+') as out:
            p = Popen([self.p4c, 'output/%s.p4' % prog , '--json', json_path],
                stdout=out, stderr=out)
            p.wait()
            assert (p.returncode == 0)

    def run_behavioral_switch(self):
        prog = 'main'
        json_path = 'output/%s.json' % prog
        commands = 'output/commands.txt'
        cmd = 'sudo {0} {1} -i0@veth0 -i1@veth2 -i 2@veth4 {2}'.format(self.switch_path,
                json_path, self.log_level)
        print cmd
        args = shlex.split(cmd)
        out_file = '{0}/bmv2.log'.format(self.directory)
        with open(out_file, 'w') as out:
            out.write('Number of packets: %d\n' % self.nb_packets)
            out.write('offered load:  %d\n' % self.offer_load)
            self.p = Popen(args, stdout=out, stderr=out, shell=False)
        assert (self.p.poll() == None)
        # wait for the switch to start
        time.sleep(2)
        # insert rules: retry 3 times if not succeed
        self.add_rules(json_path, commands, 3)

    def has_lost_packet(self):
        with open('%s/loss.csv' % self.directory, 'r') as f:
            for line in f:
                pass
            data = shlex.split(line)
            assert (len(data) == 3)
            sent = float(data[0])
            recv = float(data[1])
        return (recv < sent)


def main():
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-n', '--nb-tables', default=5, type=int,
                        help='number of tables from start')
    parser.add_argument('-s', '--tbl-size', default=32, type=int,
                        help='table size')
    args = parser.parse_args()

    nb_tables = args.nb_tables

    while(nb_tables <= 40):
        offer_load = 100000
        p = BenchmarkPipelineDepth(nb_tables, args.tbl_size, offer_load)
        # compile
        p.compile_p4_program()
        p.start()
        while (p.has_lost_packet() != True):
            offer_load += 100000
            p = BenchmarkPipelineDepth(nb_tables, args.tbl_size, offer_load)
            p.start()

        nb_tables += 5
    p.run_analyser()

if __name__=='__main__':
    main()
