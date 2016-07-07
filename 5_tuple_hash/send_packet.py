#!/usr/bin/env python

from scapy.all import *
import sys
import argparse

def generate(args):
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02") / \
        IP(src="10.0.0.1", dst="10.0.0.2") / \
        TCP(sport=args.source, dport=5678)
    hexdump(p)
    p.show()
    sendp(p, iface = args.interface)


def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth4', help="bind to specified interface")
    parser.add_argument("-s", "--source", type=int, default=1234, help="TCP source port")
    args = parser.parse_args()

    generate(args)

if __name__=='__main__':
    main()