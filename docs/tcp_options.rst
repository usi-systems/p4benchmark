TCP Options Parser
=================

This example demonstrates how to parse variable length of IP packets. The TCP
options include additional bytes to the IP packet.

Running Demo
------------

We provide a small demo to let you test the program.

* run_switch.sh: compile the P4 program and starts the switch,
  also configures the data plane by running the CLI (commands.txt)
* mpls_generator: generate a/an MPLS/IP Label packet

To run the demo:

* create virtual interfaces (need to run only if the VM has restarted)::

    sudo ../veth_setup.sh

* start the switch::

    sudo ./run_switch.sh

* to send packet::

    sudo ./send_one.py -i veth4
