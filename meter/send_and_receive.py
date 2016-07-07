#!/usr/bin/env python

from scapy.all import *
import sys
import threading
import argparse
import time

big_lock = threading.Lock()


class Receiver(threading.Thread):
    def __init__(self, interface):
        threading.Thread.__init__(self)
        self.interface = interface
        self.count = 0
        self.daemon = True

    def received(self, p):
        big_lock.acquire()
        self.count = self.count + 1
        print "%s: Received %d packets" % (self.interface, self.count)
        big_lock.release()


    def run(self):
        sniff(iface=self.interface, prn=lambda x: self.received(x))


def main():
    parser = argparse.ArgumentParser(description='MPLS label generator')
    parser.add_argument("-i", "--interface", default='veth0', help="bind to specified interface")
    parser.add_argument("-t", "--interval", type=float, default=1,
                            help="set the sending interval")
    parser.add_argument("-c", "--count", type=int, default=1,
                            help="set the number of packets sent in one interval")
    parser.add_argument("-v", "--vsize", type=int, default=10,
                            help="set the number of bytes of value")
    args = parser.parse_args()

    Receiver("veth2").start()
    Receiver("veth4").start()
    Receiver("veth6").start()

    values = 'a' * args.vsize
    p = Ether(src="aa:aa:aa:aa:aa:aa") / IP(dst="10.0.1.10") / TCP() /  values

    big_lock.acquire()
    sendp(p, iface=args.interface, inter=args.interval, count=args.count)
    big_lock.release()

    time.sleep(2)

if __name__ == '__main__':
    main()