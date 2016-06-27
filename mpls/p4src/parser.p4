#define MPLS_PROTOCOL 0x8847
#define STACK_DEPTH     300
parser start {
    return parse_ethernet;
}

header ethernet_t eth;

parser parse_ethernet {
    extract(eth);
    return select(latest.dl_type) {
        MPLS_PROTOCOL : parse_mpls_label;
        default : ingress;
    }
}

header mpls_label_t label_stack[STACK_DEPTH];

parser parse_mpls_label {
    extract(label_stack[next]);
    return select(latest.bos) {
        0 : parse_mpls_label;
        1 : ingress;
    }
}