#!/usr/bin/env python

from scapy.all import *
import sys
import argparse


def client(args):
    if args.vlan:
        eth = Ether(src="00:00:00:00:00:02", dst="00:00:00:00:00:01") / Dot1Q(vlan=1,id=6,prio=7)
        ip = IP(src="10.0.0.2", dst="10.0.0.1")
    else:
        eth = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02")
        ip = IP(src="10.0.0.1", dst="10.0.0.2")

    p = eth / ip / ICMP()
    # hexdump(p)
    p.show()
    sendp(p, iface = args.interface)

def handle(x):
    hexdump(x)

def server(args):
    sniff(iface = args.interface, prn = lambda x: handle(x))

def main():
    parser = argparse.ArgumentParser(description='receiver and sender to test P4 program')
    parser.add_argument("-s", "--server", help="run as server", action="store_true")
    parser.add_argument("-c", "--client", help="run as client", action="store_true")
    parser.add_argument("-i", "--interface", default='veth1', help="bind to specified interface")
    parser.add_argument("-v", "--vlan", default=False, action='store_true',
                        help="send a VLAN tag packet")
    args = parser.parse_args()

    if args.server:
        server(args)
    elif args.client:
        client(args)
    else:
        parser.print_help()

if __name__=='__main__':
    main()