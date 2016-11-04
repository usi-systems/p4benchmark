# dpl-benchmark

Tool to benchmark P4 Compilers and Targets

## Installation

```
pip install -r requirements.txt
python setup.py install
```

## Generate P4 Program and PCAP file for testing

* __Benchmark parse field__


The generated P4 program parses Ethernet,
PTP and a customized header containing 4 fields and each field is 16-bit wide.

```
p4benchmark --feature parse-field --fields 4
```

* __Benchmark parse header__


The generated P4 program parses Ethernet, PTP and
a customized number of headers each containing a customized number of fields.
Each field is 16-bit wide.

```
p4benchmark --feature parse-header --fields 4 --headers 4
```

* __Benchmark parse complex__


The generated P4 program parses Ethernet, PTP and
a parse graph that has the depth of 2 and each node has 2 branches.

```
p4benchmark --feature parse-complex --depth 2 --fanout 2
```

* __Benchmark action complexity__


The generated P4 program has N=2 number of set-field operations.

```
p4benchmark --feature set-field --operations 2
```

* __Benchmark header addition__


The generated P4 program adds N=2 number of headers to packets.

```
p4benchmark --feature add-header --headers 2
```

* __Benchmark header removal__


The generated P4 program removes N=2 number of headers to packets.

```
p4benchmark --feature rm-header --headers 2
```

* __Benchmark processing pipeline__


The generated P4 program applies N=2 number of tables.

```
p4benchmark --feature pipeline --tables 2 --table-size 32
```

* __Benchmark Read State__


The generated P4 program declares 1 register and performs 10 number of read operations.

```
p4benchmark --feature read-state --registers 1 --operation 10
```

* __Benchmark Write State__


The generated P4 program declares 1 register and performs 10 number of write operations.

```
p4benchmark --feature write-state --registers 1 --operation 10
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

sudo ./run_test.py --nb-headers 1 --nb-fields 4
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
```

### Run pktgen

This packet generator reads the prepared PCAP file and send `c` copies of that
packet at `t` Byte per second out of the interface `veth4`. The result is stored
in the `result` directory.

```
$ p4benchmark/pktgen/build
sudo ./p4benchmark -p ../../output/test.pcap -i veth4 -c 10000 -t 10000 -o result
```