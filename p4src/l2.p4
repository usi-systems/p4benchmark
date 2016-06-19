#include "include/headers.p4"
#include "include/parser.p4"


header_type ingress_intrinsic_metadata_t {
    fields {
        resubmit_flag : 1;              // flag distinguishing original packets
                                        // from resubmitted packets.

        ingress_global_tstamp : 48;     // global timestamp (ns) taken upon
                                        // arrival at ingress.

        mcast_grp : 16;                 // multicast group id (key for the
                                        // mcast replication table)

        deflection_flag : 1;            // flag indicating whether a packet is
                                        // deflected due to deflect_on_drop.
        deflect_on_drop : 1;            // flag indicating whether a packet can
                                        // be deflected by TM on congestion drop

        enq_qdepth : 19;                // queue depth at the packet enqueue
                                        // time.
        enq_tstamp : 32;                // time snapshot taken when the packet
                                        // is enqueued (in nsec).
        enq_congest_stat : 2;           // queue congestion status at the packet
                                        // enqueue time.

        deq_qdepth : 19;                // queue depth at the packet dequeue
                                        // time.
        deq_congest_stat : 2;           // queue congestion status at the packet
                                        // dequeue time.
        deq_timedelta : 32;             // time delta between the packet's
                                        // enqueue and dequeue time.

        mcast_hash : 13;                // multicast hashing
        egress_rid : 16;                // Replication ID for multicast
        lf_field_list : 32;             // Learn filter field list
        priority : 3;                   // set packet priority
    }
}
metadata ingress_intrinsic_metadata_t intrinsic_metadata;

counter eth_count {
    type : packets;
    instance_count : 1;
}

action _drop() {
    drop();
}

action _nop() {

}

action broadcast() {
    modify_field(intrinsic_metadata.mcast_grp, 1);
}

action mac_learn() {
    count(eth_count, 0);
    broadcast();
}

action forward(port) {
    modify_field(standard_metadata.egress_spec, port);
}

table smac {
    reads {
        ethernet.srcAddr : exact;
    }
    actions {mac_learn; _nop;}
    size : 512;
}

table dmac {
    reads {
        ethernet.dstAddr : exact;
    }
    actions {
        forward;
        broadcast;
    }
    size : 512;
}

table mcast_src_pruning {
    reads {
        standard_metadata.instance_type : exact;
    }
    actions {_nop; _drop;}
    size : 1;
}

#define CPU_MIRROR_SESSION_ID                  250

field_list copy_to_cpu_fields {
    standard_metadata;
}

action do_copy_to_cpu() {
    clone_ingress_pkt_to_egress(CPU_MIRROR_SESSION_ID, copy_to_cpu_fields);
}

table copy_to_cpu {
    actions {do_copy_to_cpu;}
    size : 1;
}

action do_cpu_encap() {
    add_header(cpu_header);
    modify_field(cpu_header.in_port, standard_metadata.ingress_port);
}

table redirect {
    reads { standard_metadata.instance_type : exact; }
    actions { _nop; do_cpu_encap; }
    size : 16;
}

control ingress {
    apply(smac);
    apply(dmac);
    apply(copy_to_cpu);
}

control egress {
    apply(redirect);
    if(standard_metadata.ingress_port == standard_metadata.egress_port) {
        apply(mcast_src_pruning);
    }
}