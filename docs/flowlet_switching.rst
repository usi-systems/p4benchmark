Flowlet Switching
=============

A flowlet is a burst of packets from the same flow followed by an idle interval.
This application parses TCP header and hashes the 5-tuple of TCP to an index
and the interval between packets could device flows to balance load among
multiple paths.

Running Demo
------------

We provide a small demo to let you test the program.

* `run_switch.sh <../../../flowlet_switching/run_switch.sh>`_: compile the
  P4 program and starts the switch, also configures the data plane by running
  the CLI `commands <../../../flowlet_switching/commands.txt>`_
* `run_test.py <../../../flowlet_switching/run_test.py>`_: Send packets to port
  3 of the switch 

To run the demo:

* create virtual interfaces (need to run only if the VM has restarted)::

    sudo ../veth_setup.sh

* start the switch::

    sudo ./run_switch.sh

* send packets::

    sudo ./run_test.py
