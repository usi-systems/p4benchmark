VXLAN
=====

This program illustrates a VTEP that encapsulates and decapsulates a VXLAN tag

The P4 program does the following:

* incoming packets are matched against a vtep table and outer headers are
  attached to the original packets
* the modified packet is forwarded in the egress pipeline

Running the demo
----------------

We provide a small demo to let you test the program. It consists of the
following scripts:

* cliser.py: sniff packets on specified port (veth5) in server 
  mode. Or send a packet to a specified port in client mode

To run the demo:

* start the switch and configure the tables::

    sudo ./run_switch.sh

* start the server::

    sudo python cliser.py -s -i veth5


* send packets::

    sudo python cliser.py -c -i veth1