MPLS Label Parser
=================

This example demonstrates the use of `add_header` and `remove_header` actions.
The application could encap a MPLS label to IP packets, swap, or strip
labels in the stack.

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

* use mpls_generator to send packet::

    sudo ./mpls_generator.py -i veth4
