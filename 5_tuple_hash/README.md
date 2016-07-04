# 5-Tuples Hash

## Description

This application is a building block that parses TCP header and hashes the 5-tuple
of TCP to an index which is used by other protocols (ECMP, CONGA, HULA, etc.) 
to balance load among multiple paths.

## Running Demo

We provide a small demo to let you test the program.

- [run_switch.sh](run_switch.sh): compile the P4 program and starts the switch,
  also configures the data plane by running the CLI [commands](commands.txt)
- [run_test.py](run_test.py): Send packets to port 3 of the switch 

To run the demo:
- create virtual interfaces (need to run only if the VM has restarted): 
`sudo ../veth_setup.sh`
- start the switch: `sudo ./run_switch.sh`
- send packet: `sudo ./run_test.py`