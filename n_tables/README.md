# Layer Forwarding

## Description

This application simply moves packets through a list of tables. Then length of
the pipeline depends on the packet field.

## Running Demo

We provide a small demo to let you test the program.

- [run_switch.sh](run_switch.sh): compile the P4 program and starts the switch,
  also configures the data plane by running the CLI [commands](commands.txt)
- [send_packet.py](send_packet): send a custom Ethernet packet to the switch

To run the demo:
- create virtual interfaces (need to run only if the VM has restarted): 
`sudo ../veth_setup.sh`
- start the switch: `sudo ./run_switch.sh`
- start tcpdump: `sudo tcpdump -i veth2`
- send_packet: `sudo ./send_packet.py -i veth4 -r 3`