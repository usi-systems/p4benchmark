import os
from subprocess import call, Popen, PIPE
import shlex
import time
import argparse

P4BENCHMARK_ROOT = os.environ.get('P4BENCHMARK_ROOT')
assert os.environ.get('P4BENCHMARK_ROOT')
assert os.environ.get('PYTHONPATH')

class BMV2Switch:
    def __init__(self,
            json_path = None,
            commands_path = None,
            log_path = "./",
            thrift_port = None,
            iface1 = 'veth2',
            iface2 = 'veth4',
            bmv2_path = os.path.join(P4BENCHMARK_ROOT, 'behavioral-model'),
            ):
        assert os.path.isfile(json_path), "bad switch json file: " + str(json_path)
        self.json_path = json_path

        assert os.path.isfile(commands_path), "bad switch commands file: " + str(commands_path)
        self.commands_path = commands_path

        assert os.path.isdir(log_path), "bad switch log dir: " + str(log_path)
        self.log_path = log_path

        self.bin_path = os.path.join(bmv2_path, 'targets/simple_switch/simple_switch')
        self.cli_path = os.path.join(bmv2_path, 'tools/runtime_CLI.py')

        self.thrift_port = thrift_port
        self.iface1 = iface1
        self.iface2 = iface2
        self.log_level = ''

    def add_rules(self, commands, retries):
        if retries == 0: return
        assert os.path.isfile(commands)
        cmd = [self.cli_path, '--json', self.json_path]
        if self.thrift_port: cmd += ['--thrift-port', str(self.thrift_port)]
        with open(commands, "r") as f:
            p = Popen(cmd, stdin=f, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            if out:
                print out
            if err or (out and "Could not" in out):
                print "Retry in 1 second"
                time.sleep(1)
                return self.add_rules(commands, retries-1)

    def kill(self):
        cmd = 'sudo pkill lt-simple_swi'
        args = shlex.split(cmd)
        p = Popen(args)
        out, err = p.communicate()
        if out:
            print out
        if err:
            print err
        self.p.wait()
        assert (self.p.poll() != None)
        time.sleep(5)

    def start(self):
        cmd = 'sudo {0} {1} -i1@{2} -i2@{3} {4}'.format(self.bin_path,
                self.json_path, self.iface1, self.iface2, self.log_level)
        if self.thrift_port: cmd += ' --thrift-port %d' % self.thrift_port
        print cmd
        args = shlex.split(cmd)
        out_file = '{0}/bmv2.log'.format(self.log_path)
        with open(out_file, 'w') as out:
            self.p = Popen(args, stdout=out, stderr=out, shell=False)
        assert (self.p.poll() == None)
        # wait for the switch to start
        time.sleep(2)
        # insert rules: retry 3 times if not succeed
        self.add_rules(self.commands_path, 3)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4 BMV2 Switch')
    parser.add_argument('-j', '--json', help='path to P4 JSON program', type=str, required=True)
    parser.add_argument('-c', '--commands', help='path to switch commands', type=str, required=True)
    parser.add_argument('-i', '--iface', help='interface to listen on', type=str, default='veth4')
    parser.add_argument('-d', '--duration', help='time (s) to run switch for', type=float, default=10)
    parser.add_argument('-t', '--thrift-port', help='thrift port to listen on', type=int, default=9091)
    args = parser.parse_args()

    sw = BMV2Switch(
            json_path = args.json,
            commands_path = args.commands,
            iface = args.iface,
            thrift_port = args.thrift_port,
            )
    sw.start()

    time.sleep(args.duration)
    sw.kill()
