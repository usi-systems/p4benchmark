#ifndef _PARSER_P4_
#define _PARSER_P4_

#define MPLS_PROTOCOL 0x8847
#define IP_PROTOCOL 0x800

#define STACK_DEPTH     10
parser start {
    return parse_ethernet;
}

header ethernet_t eth;

parser parse_ethernet {
    extract(eth);
    return select(latest.dl_type) {
        MPLS_PROTOCOL : parse_mpls_label;
        IP_PROTOCOL : parse_ipv4;
        default : ingress;
    }
}

header mpls_label_t label_stack[STACK_DEPTH];
metadata ingress_metadata_t ingress_metadata;

parser parse_mpls_label {
    extract(label_stack[next]);
    set_metadata(ingress_metadata.count, ingress_metadata.count + 1);
    return select(latest.bos) {
        0 : parse_mpls_label;
        1 : parse_ipv4;
    }
}

header ipv4_t ipv4;

parser parse_ipv4 {
    extract(ipv4);
    return ingress;
}

#endif