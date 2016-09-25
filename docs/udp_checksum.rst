UDP Checksum
============

This application simply shows the fields that is used in UDP checksum calculation.

Running Demo
------------

We provide a small demo to let you test the program.

* run_switch.sh: compile the P4 program and starts the switch,
  also configures the data plane by running the CLI (commands.txt)
* icmp.pcap: ICMP packet to feed in the switch

To run the demo:

* create virtual interfaces (need to run only if the VM has restarted)::

    sudo ../veth_setup.sh

* start the switch::

    sudo ./run_switch.sh

* start tcpdump::

    sudo tcpdump -i veth2

* to send packet::

    sudo ./send_one.py -i veth4