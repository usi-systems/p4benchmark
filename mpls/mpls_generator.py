#!/usr/bin/env python

from scapy.all import *
import sys
import argparse
import random

class MPLS(Packet): 
   name = "MPLS" 
   fields_desc =  [ BitField("label", 3, 20), 
                    BitField("exp", 0, 3), 
                    BitField("bos", 1, 1), 
                    ByteField("ttl", 1)  ] 

bind_layers(Ether, MPLS, type=0x8847)

def generate(args):
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02")
    ip = IP(src="10.0.0.1", dst="10.0.0.2")
    MIN_LABEL = 2**16
    MAX_LABEL = 2**20 - 1
    for i in range(args.repeat):
        label = random.randint(MIN_LABEL, MAX_LABEL)
        if i == args.repeat - 1:
            p = p / MPLS(bos=1, label=label)
        else:
            p = p / MPLS(bos=0, label=label)

    p = p / ip
    p.show()
    sendp(p, iface = args.interface)


def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth1', help="bind to specified interface")
    parser.add_argument("-r", "--repeat", type=int ,default=1, help="number of mpls label in the stack")
    args = parser.parse_args()

    if (args.repeat > 300):
        print "ERROR: Maximum 20 labels in the stack"
        parser.print_help()
        return
    generate(args)

if __name__=='__main__':
    main()