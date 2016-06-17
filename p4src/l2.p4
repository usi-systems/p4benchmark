#include "include/headers.p4"
#include "include/parser.p4"

action _nop() {

}

action learn_mac() {

}

table smac_tbl {
    reads {
        ethernet.srcAddr : exact;
    }
    actions {
        _nop;
        learn_mac;
    }
}


action broadcast() {

}


action forward() {

}


table dmac_tbl {
    reads {
        ethernet.dstAddr : exact;
    }
    actions {
        broadcast;
        forward;
    }
}


control ingress {
    apply(smac_tbl);
    apply(dmac_tbl);
}