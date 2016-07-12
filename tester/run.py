#!/usr/bin/env python

from multiprocessing import Process
from scapy.all import *
import sys
import argparse
import time


dpb_type = {
    0 : 'Start',
    1 : 'End',
}


class DPB(Packet):
    name = 'Data plane benchmark'
    fields = [
        ShortEnumField("end", 1, dpb_type)
    ]

bind_layers(UDP, DPB, dport=1747)


def send(args):
    eth = Ether(dst='00:00:00:00:00:02')
    ip = fuzz(IP()) 
    udp = UDP(sport=34951, dport=4789)
    p = eth / ip / udp 
    remain_bytes = args.packet_size - len(p)
    p = p / ('a' * remain_bytes)
    print 'prepare to send...'
    sendpfast(p*args.count, iface = args.ingress, pps=args.pps, mbps=args.mbps)
    last_packet = eth / ip / UDP(dport=1747) / DPB()
    # wait for burst end
    time.sleep(1)
    sendp(last_packet, iface = args.ingress)


def handle(x, output_count):
    output_count[0] += 1

def stop_sniffing(x):
    return x.haslayer(DPB)

def recv(args):
    output_count = [0]
    sniff(count=args.count, iface = args.egress,
        prn = lambda x: handle(x, output_count), 
        stop_filter= stop_sniffing,
        timeout = args.timeout)

    print 'received %d packets' % output_count[0]
    input_count = args.count
    frame_loss_rate = ( ( input_count - output_count[0] ) * 100.0 ) / input_count
    print "loss rate: %f" % frame_loss_rate

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='receiver and sender to test P4 program')
    # parser.add_argument('input', help='input PCAP file')
    parser.add_argument('-i', '--ingress', default='veth3', help='ingress interface')
    parser.add_argument('-e', '--egress', default='veth4', help='egress interface')
    parser.add_argument('--count', type=int, default=1000, help='number of frames')
    parser.add_argument('--timeout', type=int, default=120, help='sniff timeout')
    parser.add_argument('--pps', type=int, default=1000, help='sending rate pps')
    parser.add_argument('--mbps', type=int, default=1000, help='sending rate mpls')
    parser.add_argument('--packet_size', type=int, default=64, help='packet_size')
    args = parser.parse_args()

    receiver = Process(target=recv, args=(args,))
    receiver.start()

    sender = Process(target=send, args=(args,))
    sender.start()


    receiver.join()
    sender.join()
