#include "header.p4"
#include "parser.p4"

#define MAX_INST    256

header_type intrinsic_metadata_t {
    fields {
        mcast_grp : 4;
        egress_rid : 4;
        mcast_hash : 16;
        lf_field_list : 32;
        resubmit_flag : 16;
    }
}

metadata intrinsic_metadata_t intrinsic_metadata;
field_list resubmit_FL {
    standard_metadata;
    local_metadata;
}

register inner_states {
    width : 32;
    instance_count : MAX_INST;
}

action _drop() {
    drop();
}

action _nop() {

}

action forward(port) {
    modify_field(standard_metadata.egress_spec, port);
}

table forward_tbl {
    reads {
        eth.dstAddr : exact;
    } actions {
        forward;
        _drop;
    }
    size : 128;
}

action set_state() {
    register_write(inner_states, paxos_value.inst, paxos_value.px_value);
}

action get_states() {
    register_read(paxos_value.px_value, inner_states, retrieve.from + local_metadata.index);
    modify_field(local_metadata.index, local_metadata.index + 1);
}

table paxos_tbl {
    reads {
        local_metadata.px_type : exact;
    }
    actions {
        set_state;
        get_states;
        _nop;
    }
    size : 4;
}

action repeat() {
    resubmit(resubmit_FL);
}

table circle {
    reads {
        local_metadata.index : exact;
    } actions {
        _drop;
        repeat;
    }
    size : 4;
}

control ingress {
    //apply(forward_tbl);
    if (valid (paxos)) {
        apply(paxos_tbl);
        if (valid (retrieve)) {
            if (local_metadata.index < (retrieve.to - retrieve.from))
                apply(circle);
        }
    }
}

