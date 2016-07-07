#!/usr/bin/env python

from scapy.all import *
import sys
import argparse
import zlib

msgtype = {
    0 : 'PHASE1A',
    1 : 'PHASE1B',
    2 : 'PHASE2A',
    3 : 'PHASE2B',
    4 : 'DELIVER',
}

class Paxos(Packet): 
   name = "PaxosHeader" 
   fields_desc =  [ 
                    ShortEnumField("px_type", 2, msgtype), 
                    IntField("inst", 2)
                    ]

class Phase1a(Packet):
    name = "Phase1a Message"
    fields_desc =  [ 
                    ShortField("ballot", 2)
                    ]

class Phase1b(Packet):
    name = "Phase1b Message"
    fields_desc =  [ 
                    ShortField("ballot", 2), 
                    ShortField("vballot", 2), 
                    ShortField("acceptor", 0), 
                    XIntField("px_checksum", 0)
                    ]

class Phase2a(Packet):
    name = "Phase2a Message"
    fields_desc =  [ 
                    ShortField("ballot", 2), 
                    XIntField("px_checksum", 0)
                    ]

class Phase2b(Packet):
    name = "Phase2b Message"
    fields_desc =  [ 
                    ShortField("ballot", 2), 
                    ShortField("acceptor", 0), 
                    XIntField("px_checksum", 0)
                    ]

class Deliver(Packet):
    name = "Deliver Message"
    fields_desc =  [ 
                    XIntField("px_checksum", 0)
                    ]



bind_layers(UDP, Paxos, dport=0x8888)
bind_layers(Paxos, Phase1a, {'px_type' : 0})
bind_layers(Paxos, Phase1b, {'px_type' : 1})
bind_layers(Paxos, Phase2a, {'px_type' : 2})
bind_layers(Paxos, Phase2b, {'px_type' : 3})
bind_layers(Paxos, Deliver, {'px_type' : 4})

def generate(args):
    cksm =  (zlib.crc32(args.value)) % (1<<32)
    p = Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02") / \
        IP(src="10.0.0.1", dst="10.0.0.2") / \
        UDP(sport=54213)

    if args.msgtype == 0:
        p = p / Paxos(inst=args.inst) / Phase1a(ballot=args.ballot)
    if args.msgtype == 1:
        p = p / Paxos(inst=args.inst) / \
            Phase1b(ballot=args.ballot, acceptor=args.acceptor, px_checksum=cksm)
    elif args.msgtype == 2:
        p = p / Paxos(inst=args.inst) / \
                Phase2a(ballot=args.ballot, px_checksum=cksm) / args.value
    elif args.msgtype == 3:
        p = p / Paxos(inst=args.inst) / \
                Phase2b(ballot=args.ballot, acceptor=args.acceptor, px_checksum=cksm) / args.value

    hexdump(p)
    p.show()

    sendp(p, iface = args.interface)

def handle(x):
    hexdump(x)
    x.show()

def receive(args):
    sniff(iface = args.interface, prn = lambda x: handle(x))

def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth4', help="bind to specified interface")
    parser.add_argument("-v", "--value", default='AAAAAAAA', help="set value")
    parser.add_argument("--inst", type=int, default=1, help="set the instance")
    parser.add_argument('-t', "--msgtype", type=int, default=2, help="set the message type")
    parser.add_argument('-b', "--ballot", type=int, default=2, help="set the ballot value")
    parser.add_argument('-a', "--acceptor", type=int, default=2, help="set acceptor's id")
    parser.add_argument('-s', "--server", default=False, action='store_true', help="set role")

    args = parser.parse_args()

    if args.server:
        receive(args)
    else:
        generate(args)

if __name__=='__main__':
    main()