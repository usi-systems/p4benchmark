#include "header.p4"
#include "parser.p4"


action forward(port) {
    modify_field(standard_metadata.egress_spec, port);
    // If the packet is modified, whether the UDP checksum is recomputed correctly
    modify_field(udp.dstPort, 12345);
}

table forward_tbl {
    reads {
        standard_metadata.ingress_port : exact;
    }
    actions {
        forward;
        _drop;
    }
    size : 8;
}


action _drop() {
    drop();
}


control ingress {
    if (valid (ipv4))
        apply(forward_tbl);
}