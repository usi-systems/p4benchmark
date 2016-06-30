#!/usr/bin/env python

from scapy.all import *
import sys
import argparse

class Paxos(Packet): 
   name = "PaxosValue" 
   fields_desc =  [ 
                    ShortField("px_type", 2), 
                    IntField("inst", 2), 
                    ShortField("ballot", 2), 
                    ShortField("px_value", 0x0809), 
                    ]

class Ack(Packet): 
   name = "Paxos Acknowledgment" 
   fields_desc =  [ 
                    ShortField("px_type", 2), 
                    IntField("inst", 2), 
                    ShortField("ballot", 2), 
                    ShortField("px_value", 0x0809), 
                    ShortField("acpt", 0)
                    ]


bind_layers(UDP, Paxos, dport=0x8888)
bind_layers(UDP, Ack, dport=0x8889)

def generate(args):
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02") / \
        IP(src="10.0.0.1", dst="10.0.0.2") / \
        UDP(sport=54213) / \
        Paxos(px_type=args.msgtype, inst=args.inst, ballot=args.ballot)

    p.show()
    sendp(p, iface = args.interface)


def receive(args):
    sniff(iface = args.interface, prn = lambda x: hexdump(x))

def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth4', help="bind to specified interface")
    parser.add_argument("--inst", type=int, default=1, help="set the instance")
    parser.add_argument('-t', "--msgtype", type=int, default=2, help="set the message type")
    parser.add_argument('-b', "--ballot", type=int, default=2, help="set the ballot value")
    parser.add_argument('-s', "--server", default=False, action='store_true', help="set role")

    args = parser.parse_args()

    if args.server:
        receive(args)
    else:
        generate(args)

if __name__=='__main__':
    main()