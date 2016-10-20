#!/usr/bin/env python

import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse

class P4vSwitch(object):
    def start_ovsdb_server(self):
        cmd = "sudo ./ovsdb/ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile"
        print cmd
        return Popen(shlex.split(cmd))

    def start_ovs_vswitchd(self):
        cmd = "sudo ./vswitchd/ovs-vswitchd --dpdk -c 0x1 -n 4 -- unix:/usr/local/var/run/openvswitch/db.sock --pidfile"
        print cmd
        return Popen(shlex.split(cmd))

    def add_flows(self, command_file):
        with open(command_file, 'r') as fin:
            for line in fin:
                cmd = """sudo {0}/{1}""".format('utilities', line)
                print cmd
                p = Popen(shlex.split(cmd))
                p.wait()

    def stop_ovs_vswitchd(self):
        cmd = 'sudo pkill ovs-vswitchd'
    	args = shlex.split(cmd)
    	p = Popen(args)
    	p.wait()

    def stop_ovsdb_server(self):
        cmd = 'sudo pkill ovsdb-server'
    	args = shlex.split(cmd)
    	p = Popen(args)
    	p.wait()

    def run(self):
	ovsdb = self.start_ovsdb_server()
	vswitchd = self.start_ovs_vswitchd()
	time.sleep(1)
	self.add_flows('vs_commands.txt')
	self.add_flows('commands.txt')
	vswitchd.wait()
	ovsdb.wait()

    def stop_all(self):
        self.stop_ovs_vswitchd()
        self.stop_ovsdb_server()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='P4 Benchmark')
    parser.add_argument('-k', '--kill-ovs', default=False, action='store_true',
                        help='kill ovsdb server and vswitchd')
    args = parser.parse_args()
    pisces = P4vSwitch()

    if args.kill_ovs:
	pisces.stop_all()
    else:
        pisces.run()
