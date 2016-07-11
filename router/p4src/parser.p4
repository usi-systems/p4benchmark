#ifndef _PARSER_P4_
#define _PARSER_P4_

#define IP_PROTOCOL 0x800

parser start {
    return parse_ethernet;
}

header ethernet_t eth;

parser parse_ethernet {
    extract(eth);
    return select(latest.dl_type) {
        IP_PROTOCOL : parse_ipv4;
        default : ingress;
    }
}


header ipv4_t ipv4;

parser parse_ipv4 {
    extract(ipv4);
    return ingress;
}

#endif