#!/usr/bin/env python

from scapy.all import *
import sys
import argparse


def generate(args):
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02") / \
        IP(src="10.0.0.1", dst="10.0.0.2") / \
        TCP( options=[('Timestamp', (342940201L, 0L)), ('MSS', 1460),
                     ('NOP', ()), ('SAckOK', ''), ('WScale', 100)] )
    sendp(p, iface = args.interface)


def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth2', help="bind to specified interface")

    args = parser.parse_args()

    generate(args)

if __name__=='__main__':
    main()