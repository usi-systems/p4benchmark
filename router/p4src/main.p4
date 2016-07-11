#include "header.p4"
#include "parser.p4"

metadata routing_metadata_t routing;

action _drop() {
    drop();
}

action _nop() {

}

action set_outgoing_interface(port) {
    modify_field(standard_metadata.egress_spec, port);
}

action forward(port, next_hop) {
    set_outgoing_interface(port);
    modify_field(routing.next_hop, next_hop);
    modify_field(ipv4.ttl, ipv4.ttl-1);
}


table ip_lookup {
    reads {
        ipv4.dstAddr : lpm;
    } actions {
        forward;
        _drop;
    }
    size : 128;
}

action rewrite_l2(dl_src, dl_dst) {
    modify_field(eth.dl_src, dl_src);
    modify_field(eth.dl_dst, dl_dst);
}

table neighbor {
    reads {
        routing.next_hop : exact;
    } actions {
        rewrite_l2;
        _nop;
    }
    size : 128;
}

control ingress {
    apply(ip_lookup);
    apply(neighbor);
}