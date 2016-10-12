# dpl-benchmark

Tool to benchmark P4 Compilers and Targets

## Install Dependencies

```
sudo ./setup.sh
```

## Generate P4 Program and PCAP file for testing

The following command will generate a P4 program that parses Ethernet, IP, UDP
and 2 user-defined headers. Each header contains 4 fields and each field is
16-bit wide.

```
python generate_p4_program.py --parser --headers 2 --fields 4
```

## Generated Files

The `output` directory contains:
```
$ ls output
commands.txt  main.p4  run_switch.sh  run_test.py  test.pcap
```

1. `main.p4`        The desired program to benchmark a particular feature of the P4 target
2. `test.pcap`      Sample packet crafted to match the parser or tables
3. `run_switch.sh`  Script to run and configure bmv2
4. `commands.txt`   Match-action rules for tables
5. `run_test.py`    Python packet generator and receiver


## Run Behavioral Target

```
cd output
./run_switch
```

## Run Python packet generator

In another terminal, run:

```
cd output
sudo ./run_test.py --nb-headers 2 --nb-fields 4
```

## PKTGEN (Send PCAP file)

Or, you could use a high performance packet generator that sends the prepared
PCAP file and sniffs for returning packets

### Build

```
cd pktgen
mkdir build
cd build
cmake ..
make
``

### Run pktgen

This packet generator reads the prepared PCAP file and send `c` copies of that
packet at `t` Byte per second out of the interface `veth4`. The result is stored
in the `result` directory.

```
$ p4benchmark/pktgen/build

sudo ./p4benchmark -p ../../output/test.pcap -i veth4 -c 10000 -t 10000 -o result
```