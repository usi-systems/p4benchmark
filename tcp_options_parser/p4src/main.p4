#include "include/headers_tcp.p4"
#include "include/parser_tcp.p4"
#include "include/intrinsic.p4"

action forward(port) {
    modify_field(standard_metadata.egress_spec, port);
}

action _drop() {
    drop();
}

table forward_tbl {
    reads {
        ethernet.dstAddr : exact;
    } actions {
        forward;
        _drop;
    }
    size : 1024;
}
control ingress {
    apply(forward_tbl);
}
