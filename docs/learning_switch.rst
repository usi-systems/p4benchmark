Learning Switch
===============

This program illustrates a learning switch coupled with a software controller
to populate MAC address tables at runtime

Description
-----------

incoming packets are mirrored to the CPU port using the *clone_ingress_pkt_to_egress*
action primitive::

    #define CPU_MIRROR_SESSION_ID   250

    field_list copy_to_cpu_fields {
        standard_metadata;
    }

    action do_copy_to_cpu() {
        clone_ingress_pkt_to_egress(CPU_MIRROR_SESSION_ID, copy_to_cpu_fields);
    }

    // (commands.txt) MIRROR_ID 250, forward to port 1
    mirroring_add 250 1


packets mirrored to CPU are encapsulated with a custom `cpu_header` which
includes 1 field: `in_port` (1 byte, set to the ingress_port of the packet)::

    header_type cpu_header_t {
        fields {
            in_port : 8;
        }
    }

    action do_cpu_encap() {
        add_header(cpu_header);
        modify_field(cpu_header.in_port, standard_metadata.ingress_port);
    }

the original packet is forwarded or broadcast in the egress pipeline::

    action broadcast() {
        modify_field(intrinsic_metadata.mcast_grp, 1);
    }

    action forward(port) {
        modify_field(standard_metadata.egress_spec, port);
    }

The controller (controller.py) received packets on port 1, and send forwarding
rules to add them to the forwarding table of the switch::

    def send_command(args, addr, port):
        dmac_rule = 'table_add dmac forward %s => %d\n' % (addr, port)
        smac_rule = 'table_add smac _nop %s =>\n' % addr


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