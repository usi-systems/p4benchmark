#include "header.p4"
#include "parser.p4"
#include "mpls.p4"

action _drop() {
    drop();
}

action forward(port) {
    modify_field(standard_metadata.egress_spec, port);
}

table forward_tbl {
    reads {
        eth.dl_dst : exact;
    } actions {
        forward;
        _drop;
    }
    size : 1024;
}

control ingress {
    apply(forward_tbl);
    if (valid (label_stack[0])) {
        if (label_stack[0].ttl > 0)
            apply(LFIB);
    } else if (valid (ipv4)) {
        if (ipv4.ttl > 0)
            apply(IPFIB);
    }
}