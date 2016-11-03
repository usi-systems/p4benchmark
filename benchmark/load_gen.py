import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse
import string

assert os.environ.get('P4BENCHMARK_ROOT')
assert os.environ.get('PYTHONPATH')
P4BENCHMARK_ROOT = os.environ.get('P4BENCHMARK_ROOT')

class SendB2B:
    def __init__(self,
            pcap_path = None,
            count = 100000,
            out_path = './',
            recv_iface = 'veth4',
            send_iface = 'veth2',
            pktgen_path = os.path.join(P4BENCHMARK_ROOT, 'pktgen')
            ):

        assert os.path.isdir(pktgen_path), "bad switch sendb2b dir: " + str(pktgen_path)
        self.sendb2b_bin = os.path.join(pktgen_path, 'build', 'sendb2b')
        assert os.path.isfile(self.sendb2b_bin), "bad sendb2b binary: %s" % self.sendb2b_bin

        assert os.path.isfile(pcap_path), "bad pcap file: " + str(pcap_path)
        self.pcap_path = pcap_path

        self.out_path = out_path
        self.count = count
        self.send_iface = send_iface
        self.recv_iface = recv_iface
        self.timeout = 50

    def send_stats(self):
        with open(self.loss_path) as f:
            lines = filter(lambda l: len(l), map(string.strip, f.readlines()))
        data = shlex.split(lines[-1])
        assert (len(data) == 5)
        sent, recv, lost, tput, duration = map(float, data)
        return (sent, recv, lost, tput, duration)

    def lost_count(self):
        return self.send_stats()[2]

    def has_lost_packet(self):
        return self.lost_count()

    def results(self):
        with open(self.results_path) as f:
            lines = filter(lambda l: len(l), map(string.strip, f.readlines()))
        return map(lambda l: map(float, l.split()), lines)

    def run(self):
        cmd = 'sudo {0} -p {1} -t {2}'.format(self.sendb2b_bin,
            self.pcap_path, self.timeout)
        if self.recv_iface: cmd += ' -i %s' % self.recv_iface
        if self.send_iface: cmd += ' -s %s' % self.send_iface
        if self.count is not None: cmd += ' -c %d' % self.count
        print cmd
        args = shlex.split(cmd)

        self.results_path = os.path.join(self.out_path, 'results_raw.tsv')
        self.loss_path = os.path.join(self.out_path, 'loss.dat')
        results_file = open(self.results_path, 'w')
        loss_file = open(self.loss_path, 'w')

        self.p = Popen(args, stdout=results_file, stderr=loss_file)
        self.p.wait()

        stdout, stderr = self.p.communicate()
        results_file.close()
        loss_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load Generator')
    parser.add_argument('-c', '--count', help='number of packets to send to switch', type=int, default=100000)
    parser.add_argument('-p', '--pcap', help='path to pcap file', type=str, required=True)
    parser.add_argument('-i', '--iface', help='interface to send packets to', type=str, default='veth4')
    args = parser.parse_args()

    pg = SendB2B(
            pcap_path = args.pcap,
            count = args.count,
            send_iface = args.iface,
            )
    pg.run()

    if pg.has_lost_packet():
        sent, recv = pg.send_stats()[:2]
        print "has_lost_packet"
        print "sent:", sent, "recv:", recv

    print pg.results()
