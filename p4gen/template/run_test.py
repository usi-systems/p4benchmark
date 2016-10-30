#!/usr/bin/env python

import time

P4BENCH_PORT = 0x9091

import random
import argparse

import threading
from scapy.all import sniff, wrpcap, rdpcap
from scapy.all import Ether, IP, IPv6, TCP, UDP
from scapy.all import Packet, ShortField, XBitField, bind_layers

class PTP(Packet):
    """Precision Time Protocol"""
    name = "PTP protocol"
    fields_desc = [
        XBitField('type_', 0x10, 8),
        XBitField('version', 0x02, 8),
        ShortField('messageLength', 0x36),
        XBitField('subdomain', 0x00, 8),
        ShortField('flags', 0),
        XBitField('correction', 0x00, 48),
        XBitField('clockIdentity', 0x008063FFFF0009BA, 64),
        ShortField('sourcePortID', 1),
        ShortField('sequenceID', 0x9E48),
        XBitField('control', 0x05, 8),
        XBitField('logMessagePeriod', 0x0F, 8),
        XBitField('originTimestamp', 0x000045B111510472F9C1, 80)
    ]

bind_layers(UDP, PTP, dport=319)
bind_layers(UDP, PTP, dport=320)


features = {
    0 : 'PARSER',
    1 : 'STATE',
    2 : 'PIPELINE',
    3 : 'PACKET_ADD',
    4 : 'PACKET_RM',
    5 : 'PACKET_MOD',
}

class PacketQueue:
    def __init__(self):
        self.pkts = []
        self.lock = threading.Lock()
        self.ifaces = set()

    def add_iface(self, iface):
        self.ifaces.add(iface)

    def get(self):
        self.lock.acquire()
        if not self.pkts:
            self.lock.release()
            return None, None
        pkt = self.pkts.pop(0)
        self.lock.release()
        return pkt

    def add(self, iface, pkt):
        if iface not in self.ifaces:
            return
        self.lock.acquire()
        self.pkts.append( (iface, pkt) )
        self.lock.release()

queue = PacketQueue()

def pkt_handler(pkt, iface):
    if IPv6 in pkt:
        return
    pkt.show()
    queue.add(iface, pkt)

class SnifferThread(threading.Thread):
    def __init__(self, iface, handler = pkt_handler):
        threading.Thread.__init__(self)
        self.iface = iface
        self.handler = handler

    def run(self):
        sniff(
            iface = self.iface,
            prn = lambda x: self.handler(x, self.iface)
        )

class PacketDelay:
    def __init__(self, bsize, bdelay, imin, imax, num_pkts = 100):
        self.bsize = bsize
        self.bdelay = bdelay
        self.imin = imin
        self.imax = imax
        self.num_pkts = num_pkts
        self.current = 1

    def __iter__(self):
        return self

    def next(self):
        if self.num_pkts <= 0:
            raise StopIteration
        self.num_pkts -= 1
        if self.current == self.bsize:
            self.current = 1
            return random.randint(self.imin, self.imax)
        else:
            self.current += 1
            return self.bdelay

class MemTest(Packet):
    name = "P4Bench Message for MemTest"
    fields_desc =  [
        XBitField("op", 0x1, 4),
        XBitField("index", 0x1, 12),
        XBitField("data", 0xf1f2f3f4, 32),
    ]


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='run_test.py')
    parser.add_argument('-n', '--nb-packets', default=10, type=int,
                        help='Send [n] packets to the switch')
    parser.add_argument('-c', '--nb-headers', default=1, type=int,
                        help='Add [c] P4Bench headers to each packet')
    parser.add_argument('--feature', default=0, type=int,
                        help='P4 benchmark feature')
    parser.add_argument('--register-op', default=0, type=int,
                        help='Register operation type')
    parser.add_argument('--register-index', default=0, type=int,
                        help='Register index')
    parser.add_argument('--register-value', default=0, type=int,
                        help='Register value')
    parser.add_argument('-f', '--nb-fields', default=1, type=int,
                        help='Add [f] fields to each P4Bench header')
    parser.add_argument('--random-dport',
                        help='Use a random TCP dest port for each packet',
                        action="store_true", default=False)
    args = parser.parse_args()

    pkts = rdpcap('test.pcap')
    pkt = pkts[0]

    port_map = {
        0: "veth0",
        1: "veth2",
        2: "veth4",
    }

    iface_map = {}
    for p, i in port_map.items():
        iface_map[i] = p

    queue.add_iface("veth2")
    queue.add_iface("veth4")

    for p, iface in port_map.items():
        t = SnifferThread(iface)
        t.daemon = True
        t.start()

    import socket

    send_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                                socket.htons(0x03))
    send_socket.bind((port_map[0], 0))

    # wait for receiving threads start
    time.sleep(1)

    delays = PacketDelay(10, 5, 25, 100, args.nb_packets)
    ports = []
    print "Sending", args.nb_packets, "packets ..."
    for d in delays:
        # pkt.show()
        send_socket.send(str(pkt))
        time.sleep(d / 1000.)

    # time.sleep(1)

    iface, pkt = queue.get()
    while pkt:
        ports.append(iface_map[iface])
        iface, pkt = queue.get()
    # print ports
    print "DISTRIBUTION..."
    for p in port_map:
        c = ports.count(p)
        print "port {}: {:>3} [ {:>5}% ]".format(p, c, 100. * c / args.nb_packets)
