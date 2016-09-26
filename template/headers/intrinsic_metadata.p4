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
