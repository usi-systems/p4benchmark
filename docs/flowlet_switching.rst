Flowlet Switching
=================

A flowlet is a burst of packets from the same flow followed by an idle interval.
This application parses TCP header and hashes the 5-tuple of TCP to an index
and the interval between packets could device flows to balance load among
multiple paths.

Description
-----------

The tcp_hash is calculated using 5-tuple from TCP header to generate a hash key::

    // Expecting 8K entry in the flowlet_table
    #define FLOW_WIDTH 13

    field_list l3_hash_fields {
        ipv4.srcAddr;
        ipv4.dstAddr;
        ipv4.protocol;
        tcp.srcPort;
        tcp.dstPort;
    }

    field_list_calculation tcp_hash {
        input {
            l3_hash_fields;
        }
        algorithm : crc16;
        output_width : FLOW_WIDTH;
    }

The `find_flow_let_offset` action stores the index in flow_offset metadata::

    action find_flowlet_offset() {
        modify_field_with_hash_based_offset(ingress_metadata.flow_offset, 0,
                                            tcp_hash, FLOW_WIDTH);

Then, it indexes into the registers `last_seen` to get the previous timestamp
that a packet from the same flow has been received, and  `flowlet_id` from
the flowlet_ids` register::

        register_read(ingress_metadata.last_time, last_seen,
            ingress_metadata.flow_offset);

        register_read(ingress_metadata.flowlet_id, flowlet_ids,
            ingress_metadata.flow_offset);

The action then computes the inter-packet-gap (ipg) time of the current flow which
is used later to decide the packet is belonged to the same flowlet_id or a new one.
The current timestamp is stored in the register for processing the next packet::

        modify_field(ingress_metadata.ipg,
            intrinsic_metadata.ingress_global_timestamp -
            ingress_metadata.last_time);
        register_write(last_seen, ingress_metadata.flow_offset,
            intrinsic_metadata.ingress_global_timestamp);

If the igp is greater than the threshold TIME_GAP, the a new flowlet_id is created::

    if (ingress_metadata.ipg > TIME_GAP) {
        apply(new_flowlet_tbl);
    }


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
