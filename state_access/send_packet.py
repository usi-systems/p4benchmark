#!/usr/bin/env python

from scapy.all import *
import sys
import argparse

class Paxos(Packet): 
   name = "PaxosValue" 
   fields_desc =  [ 
                    ShortField("px_type", 2), 
                    IntField("inst", 2), 
                    IntField("px_value", 1234), 
                    ]

class Retrieve(Packet): 
   name = "PaxosRetrieve" 
   fields_desc =  [ 
                    ShortField("px_type", 6), 
                    IntField("from_inst", 2), 
                    IntField("to_inst", 10), 
                    ]

bind_layers(UDP, Paxos, dport=0x8888)
bind_layers(UDP, Retrieve, dport=0x8888)

def generate(args):
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02") / \
        IP(src="10.0.0.1", dst="10.0.0.2") / \
        UDP(sport=54213)
    if args.set:
        p = p / Paxos(inst=args.inst)
    else:
        p = p / Retrieve(from_inst=args.from_inst, to_inst=args.to_inst)

    p.show()
    sendp(p, iface = args.interface)


def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth4', help="bind to specified interface")
    parser.add_argument("--inst", type=int, default=1, help="set the instance")
    parser.add_argument('-f', "--from_inst", type=int, default=2, help="set the start instance")
    parser.add_argument('-t', "--to_inst", type=int, default=10, help="set the end instance")
    parser.add_argument("-s", "--set", default=False, action='store_true',
                        help="Paxos message")

    args = parser.parse_args()

    generate(args)

if __name__=='__main__':
    main()