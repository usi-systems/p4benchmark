#include "header.p4"
#include "parser.p4"

#define MAX_INST    256

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
}

action set_state() {
    register_write(inner_states, paxos_value.inst, paxos_value.px_value);
}

action get_states() {
    register_read(paxos_value.px_value, inner_states, retrieve.from);
}

table paxos_tbl {
    reads {
        paxos.px_type : exact;
    }
    actions {
        set_state;
        get_states;
        _nop;
    }
}

control ingress {
    //apply(forward_tbl);
    if (valid (paxos)) {
        apply(paxos_tbl);
    }
}