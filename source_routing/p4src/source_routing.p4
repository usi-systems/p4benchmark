#include "header.p4"
#include "parser.p4"
action _drop() {
    drop();
}

action _nop() {

}

action forward() {
    modify_field(standard_metadata.egress_spec, ports[0].port);
}

table forward_tbl {
    reads {
        easy_route.num_port : exact;
    }
    actions {
        forward;
        _drop;
    }
    size : 2;
}
control ingress {
    apply(forward_tbl);
}