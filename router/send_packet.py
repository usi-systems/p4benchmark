#!/usr/bin/env python

from scapy.all import *
import sys
import argparse

def generate(args):
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02")
    ip = IP(src="172.16.1.100", dst="10.0.0.2")
    p = p / ip
    p.show()
    sendp(p, iface = args.interface)


def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth1', help="bind to specified interface")
    args = parser.parse_args()

    generate(args)

if __name__=='__main__':
    main()