#!/usr/bin/env python

from scapy.all import *
import sys
import argparse
import struct
import os
import subprocess
import time


mac_table = {}

def die(message):
    print message


def add_rules(cli_path, json_path, port_number, commands, retries):
    if retries > 0:
        cmd = [cli_path, json_path, str(port_number)]
        if os.path.isfile(commands):
            with open(commands, "r") as f:
                p = subprocess.Popen(cmd, stdin=f, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                if out:
                    print out
                    if "Could not" in out:
                        print "Retry in 1 second"
                        time.sleep(1)
                        return add_rules(cli_path, json_path, port_number, commands, retries-1)
                if err:
                    time.sleep(1)
                    return add_rules(cli_path, json_path, port_number, commands, retries-1)
        else:
            print cmd
            p = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate(commands)
            if out:
                print out
                if "Could not" in out:
                    time.sleep(1)
                    return add_rules(cli_path, json_path, port_number, commands, retries-1)
            if err:
                time.sleep(1)
                return add_rules(cli_path, json_path, port_number, commands, retries-1)
    else:
        die("Cannot connect to switches")


def send_command(args, addr, port):
    dmac_rule = 'table_add dmac forward %s => %d\n' % (addr, port)
    smac_rule = 'table_add smac _nop %s =>\n' % addr
    add_rules(args.cli, args.json, args.port, dmac_rule, 1)
    add_rules(args.cli, args.json, args.port, smac_rule, 1)


def handle(x, args):
    eth = x['Ethernet']
    if eth.type == 0x806:
        x.show()
        if Padding in x:
            in_port = ord(x[Padding].load)
            print "src %s, in_port %d" % (eth.src, in_port)
            if eth.src not in mac_table:
                mac_table[eth.src] = in_port
                send_command(args, eth.src, in_port)


def server(args):
    sniff(iface = args.interface, prn = lambda x: handle(x, args))


def main():
    parser = argparse.ArgumentParser(description='receiver and sender to test P4 program')
    parser.add_argument("-i", "--interface", default='s1-eth1', help="bind to specified interface")
    parser.add_argument("-j", "--json", default='l2.json', help="input jason file")
    parser.add_argument("-p", "--port", default='22222', help="thrift port")
    args = parser.parse_args()
    args.cli = "/home/vagrant/bmv2/targets/simple_switch/sswitch_CLI"
    server(args)


if __name__=='__main__':
    main()