#!/usr/bin/env python

from scapy.all import *
import sys
import argparse

def generate(args):
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02") / \
        IP(src="10.0.0.1", dst="10.0.0.2") / \
        UDP(sport=7463, dport=3237) / 'HELLO WORLD'
    hexdump(p)
    p.show()

    sendp(p, iface = args.interface)

def handle(x):
    hexdump(x)
    x.show()

def receive(args):
    sniff(iface = args.interface, prn = lambda x: handle(x))

def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth4', help="bind to specified interface")
    parser.add_argument('-s', "--server", default=False, action='store_true', help="set role")

    args = parser.parse_args()

    if args.server:
        receive(args)
    else:
        generate(args)

if __name__=='__main__':
    main()