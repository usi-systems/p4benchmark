5-Tuples Hash
=============

This application is a building block that parses TCP header and hashes the 5-tuple
of TCP to an index which is used by other protocols (ECMP, CONGA, HULA, etc.) 
to balance load among multiple paths.

The fields used to generate the hash key is declared like below::


    field_list l3_hash_fields {
        ipv4.srcAddr;
        ipv4.dstAddr;
        ipv4.protocol;
        tcp.srcPort;
        tcp.dstPort;
    }

The `l3_hash_fields` is used to compute the value for the `tcp_flow` variable,
using the `crc16` hash algorithm and the output is truncated to 10 bits::

    #define HASH_OUTPUT_WIDTH 10

    field_list_calculation tcp_flow {
        input {
            l3_hash_fields;
        }
        algorithm : crc16;
        output_width : HASH_OUTPUT_WIDTH;
    }

The `tcp_flow` later is used to calculate the `hash_index` in a compound action::

    // hash_index = (base_index + tcp_flow) % table_size
    action hash_to_index(base_index, table_size) {
        modify_field_with_hash_based_offset(routing_metadata.hash_index, base_index,
                                            tcp_flow, table_size);
    }


Running Demo
------------

We provide a small demo to let you test the program.

* `run_switch.sh <../../../5_tuple_hash/run_switch.sh>`_: compile the P4 program
  and starts the switch, also configures the data plane by running the CLI `commands <../../../5_tuple_hash/commands.txt>`_
* `run_test.py <../../../5_tuple_hash/run_test.py>`_: Send packets to port 3 of the switch 

To run the demo:

* create virtual interfaces (need to run only if the VM has restarted)::

    sudo ../veth_setup.sh

* start the switch::

    sudo ./run_switch.sh

* send packets::

    sudo ./run_test.py
