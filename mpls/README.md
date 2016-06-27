# MPLS Label Parser

## Description

This application either encaps a MPLS label to IP packets, swaps, or strips
labels in the stack

## Running Demo

We provide a small demo to let you test the program.

- [run_switch.sh](run_switch.sh): compile the P4 program and starts the switch,
  also configures the data plane by running the CLI [commands](commands.txt)
- [mpls_generator.py](mpls_generator.py): generate a/an MPLS/IP Label packet

To run the demo:
- create virtual interfaces (need to run only if the VM has restarted): 
`sudo ../veth_setup.sh`
- start the switch: `sudo ./run_switch.sh`
- use mpls_generator to send packet: `sudo ./mpls_generator.py -i veth4`
