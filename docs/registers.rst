Registers
=========

This application exercises read and write to registers. The application allows to
read a range of elements in the registers.

Running Demo
------------

We provide a small demo to let you test the program.

* run_switch.sh: compile the P4 program and starts the switch,
  also configures the data plane by running the CLI (commands.txt)
* send_packet.py: generate packets to write or read the registers

To run the demo:

* create virtual interfaces (need to run only if the VM has restarted)::

    sudo ../veth_setup.sh

* start the switch::

    sudo ./run_switch.sh

* send a packet::

    sudo ./send_packet.py -i veth4