#!/bin/bash


BMV2_PATH=${P4BENCHMARK_ROOT:?}/behavioral-model
P4C_BM_PATH=$P4BENCHMARK_ROOT/p4c-bm
P4C_BM_SCRIPT=$P4C_BM_PATH/p4c_bm/__main__.py


PROG="main"

set -m
$P4C_BM_SCRIPT $PROG.p4 --json $PROG.json

if [ $? -ne 0 ]; then
echo "p4 compilation failed"
exit 1
fi

SWITCH_PATH=$BMV2_PATH/targets/simple_switch/simple_switch

CLI_PATH=$BMV2_PATH/tools/runtime_CLI.py

sudo echo "sudo" > /dev/null
sudo $SWITCH_PATH >/dev/null 2>&1
sudo $SWITCH_PATH $PROG.json \
    -i 0@veth0 -i 1@veth2 -i 2@veth4 -i 3@veth6 -i 4@veth8 \
    &
    # --log-console &

sleep 2
echo "**************************************"
echo "Sending commands to switch through CLI"
echo "**************************************"
$CLI_PATH --json $PROG.json < commands.txt
echo "READY!!!"
fg