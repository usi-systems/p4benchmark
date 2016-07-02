#include "header.p4"
#include "parser.p4"
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
        eth.dl_dst : exact;
    } actions {
        forward;
        _drop;
    }
    size : 1024;
}
control ingress {
    apply(forward_tbl);
}