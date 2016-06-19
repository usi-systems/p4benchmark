#!/usr/bin/env python

from subprocess import Popen, PIPE

commands = """sudo mn -c
sudo killall simple_switch"""

for cmd in commands.splitlines():
    sp = Popen(cmd.split(), stdout=PIPE) 
    output, err = sp.communicate()
    if output:
        print output
    if err:
        print err.output