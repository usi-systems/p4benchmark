NAT
===

This program illustrates a NAT device coupled with a software controller
to populate NAT table at runtime

The P4 program does the following:

* incoming packets are mirrored to the CPU port using the
  `clone_ingress_pkt_to_egress` action primitive
* the original packet is forwarded or broadcast in the egress pipeline

Running the demo
----------------

We provide a small demo to let you test the program. It consists of the
following scripts:

* run_switch.sh: compile the P4 program and starts the switch,
  also configures the data plane by running the CLI (commands.txt)
* controller.py: sniff packets on port 1 (s1-eth1) and install 
  rule to map private to public IP addresses.

To run the demo

* start the switch and configure the tables and the mirroring session::

    sudo ./run_switch.sh

* start the controller::

    sudo python controller.py -i s1-eth1

* start terminal on h2::

    Mininet> xterm h2