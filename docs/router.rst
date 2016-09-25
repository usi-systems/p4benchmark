Router
======

This application illustrates L3 forwarding router. Packets are routed based on
the destination IP address.

Running Demo
------------

We provide a small demo to let you test the program.

* run_switch.sh: compile the P4 program and starts the switch,
  also configures the data plane by running the CLI (commands.txt)

To run the demo:

* create virtual interfaces (need to run only if the VM has restarted)::

    sudo ../veth_setup.sh

* start the switch::

    sudo ./run_switch.sh

* start tcpdump::

    sudo tcpdump -i veth2

* to send packet::

    sudo ./send_packet.py -i veth4