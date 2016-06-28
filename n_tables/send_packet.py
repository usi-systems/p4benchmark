#!/usr/bin/env python

from scapy.all import *
import sys
import argparse

class Custom(Packet): 
   name = "Custom" 
   fields_desc =  [ XByteField("repeat", 0xf) ]

bind_layers(Ether, Custom, type=0x9999)

def generate(args):
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02") / Custom(repeat=args.repeat)
    hexdump(p)
    p.show()
    sendp(p, iface = args.interface)


def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth4', help="bind to specified interface")
    parser.add_argument("-r", "--repeat", type=int, default=1,
                            help="set the length of processing pipeline")
    args = parser.parse_args()

    generate(args)

if __name__=='__main__':
    main()