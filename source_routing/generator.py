#!/usr/bin/env python

from scapy.all import *
import sys
import argparse


class EasyRoute(Packet):
    name = "EasyRoute "
    fields_desc = [ XIntField("num_port", 0x0)]

class EasyPort(Packet):
    name = "EasyPort "
    fields_desc = [ XShortField("port", 0x1)]

def generate(args):
    eth = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02")
    ip = IP(src="10.0.0.1", dst="10.0.0.2")
    tcp = TCP(dport=6900)

    route = EasyRoute(num_port=args.ports)

    p = eth / ip / tcp / route

    for i in range(args.ports, 0, -1):
        p = p / EasyPort(port=i)

    # hexdump(p)
    p.show()
    sendp(p, iface = args.interface)


def main():
    parser = argparse.ArgumentParser(description='receiver and sender to test P4 program')
    parser.add_argument("-i", "--interface", default='veth1', help="bind to specified interface")
    parser.add_argument("-n", "--ports", type=int ,default=1, help="number of port")
    args = parser.parse_args()

    generate(args)

if __name__=='__main__':
    main()