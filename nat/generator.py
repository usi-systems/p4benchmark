#!/usr/bin/env python

from scapy.all import *
import sys
import argparse


def generate_response(args):
    eth = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02")
    ip = IP(src="172.217.19.164", dst="77.57.59.138")
    udp = UDP(dport=34343)

    p = eth / ip / udp

    # hexdump(p)
    p.show()
    sendp(p, iface = args.interface)



def generate(args):
    eth = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02")
    ip = IP(src="10.0.0.1", dst="172.217.19.164")
    udp = UDP(dport=6900)

    p = eth / ip / udp

    # hexdump(p)
    p.show()
    sendp(p, iface = args.interface)


def main():
    parser = argparse.ArgumentParser(description='receiver and sender to test P4 program')
    parser.add_argument("-i", "--interface", default='eth0', help="bind to specified interface")
    parser.add_argument("-r", "--response", default=False, action='store_true',
        help="generate response message")
    args = parser.parse_args()
    if (args.response):
        generate_response(args)
    else:
        generate(args)

if __name__=='__main__':
    main()