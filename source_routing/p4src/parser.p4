parser start {
    return parse_ethernet;
}

header ethernet_t eth;
header ipv4_t ipv4;
header tcp_t tcp;

#define IPV4_PROTOCOL 0x800

parser parse_ethernet {
    extract(eth);
    return select(latest.dl_type) {
        IPV4_PROTOCOL : parse_ipv4;
        default : ingress;
    }
}

#define TCP_PROTOCOL 06

parser parse_ipv4 {
    extract(ipv4);
    return select(latest.protocol) {
        TCP_PROTOCOL : parse_tcp;
        default : ingress;
    }
}

#define EASY_ROUTE_PORT 6900

parser parse_tcp {
    extract(tcp);
    return select(latest.dstPort) {
        EASY_ROUTE_PORT : parse_easy_route;
        default : ingress;
    }
}

#include "source_routing_parser.p4"