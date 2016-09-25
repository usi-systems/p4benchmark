Learning Switch
===============

This program illustrates a learning switch coupled with a software controller
to populate MAC address tables at runtime

Description
-----------

The P4 program does the following:

* incoming packets are mirrored to the CPU port using the *clone_ingress_pkt_to_egress* action primitive
* packets mirrored to CPU are encapsulated with a custom `cpu_header` which
  includes 1 field: `in_port` (1 byte, set to the ingress_port of the packet)
* the original packet is forwarded or broadcast in the egress pipeline

Running the demo
----------------

We provide a small demo to let you test the program. It consists of the
following scripts:

* `run_switch.sh <../../../learning_switch/run_switch.sh>`_ : compile the P4 program and starts the switch,
  also configures the data plane by running the CLI `commands <../../../learning_switch/commands.txt>`_
* `controller.py <../../../learning_switch/controller.py>`_ : sniff packets on port 1 (s1-eth1), learn MAC 
  addresses and configure the switch at runtime

To run the demo:

* start the switch and configure the tables and the mirroring session::

    sudo ./run_switch.sh

* start the controller::

    sudo python controller.py

* send packets::

    Mininet> h2 ping h3