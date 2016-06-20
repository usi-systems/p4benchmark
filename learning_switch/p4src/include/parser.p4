#ifndef _PARSER_P4_
#define _PARSER_P4_


header ethernet_t ethernet;
header ipv4_t ipv4;
header ipv6_t ipv6;
header icmp_t icmp;
header tcp_t tcp;
header udp_t udp;
header arp_t arp;
header cpu_header_t cpu_header;


parser start {
    return parse_ethernet;
}

#define ETHERTYPE_VLAN         0x8100
#define ETHERTYPE_IPV4         0x0800
#define ETHERTYPE_IPV6         0x86dd
#define ETHERTYPE_ARP          0x0806
#define ETHERTYPE_RARP         0x8035

#define PARSE_ETHERTYPE                                    \
        ETHERTYPE_IPV4 : parse_ipv4;                       \
        ETHERTYPE_IPV6 : parse_ipv6;                       \
        ETHERTYPE_ARP : parse_arp;                         \
        ETHERTYPE_RARP : parse_arp;                        \
        default : ingress


parser parse_ethernet {
    extract(ethernet);
    return select(latest.etherType) {
        ETHERTYPE_VLAN : parse_vlan;                       \
        PARSE_ETHERTYPE;
    }
}


#define VLAN_DEPTH 2
header vlan_tag_t vlan_tag_[VLAN_DEPTH];

parser parse_vlan {
    extract(vlan_tag_[0]);
    return select(latest.etherType) {
        PARSE_ETHERTYPE;
    }
}


#define IP_PROTOCOLS_ICMP              1
#define IP_PROTOCOLS_TCP               6
#define IP_PROTOCOLS_UDP               17
#define IP_PROTOCOLS_CPUP              99

field_list ipv4_checksum_list {
        ipv4.version;
        ipv4.ihl;
        ipv4.diffserv;
        ipv4.totalLen;
        ipv4.identification;
        ipv4.flags;
        ipv4.fragOffset;
        ipv4.ttl;
        ipv4.protocol;
        ipv4.srcAddr;
        ipv4.dstAddr;
}

field_list_calculation ipv4_checksum {
    input {
        ipv4_checksum_list;
    }
    algorithm : csum16;
    output_width : 16;
}

calculated_field ipv4.hdrChecksum  {
    // verify ipv4_checksum if (ipv4.ihl == 5);
    update ipv4_checksum if (ipv4.ihl == 5);
}


parser parse_ipv4 {
    extract(ipv4);
    return select(latest.protocol) {
        IP_PROTOCOLS_ICMP : parse_icmp;
        IP_PROTOCOLS_TCP : parse_tcp;
        IP_PROTOCOLS_UDP : parse_udp;
        default: ingress;
    }
}


parser parse_ipv6 {
    extract(ipv6);
    return select(latest.nextHdr) {
        IP_PROTOCOLS_TCP : parse_tcp;
        IP_PROTOCOLS_UDP : parse_udp;
        default: ingress;
    }
}


parser parse_icmp {
    extract(icmp);
    return ingress;
}


parser parse_tcp {
    extract(tcp);
    return ingress;
}


parser parse_udp {
    extract(udp);
    return ingress;
}


parser parse_arp {
    extract(arp);
    return select(latest.pro) {
        IP_PROTOCOLS_CPUP : parse_cpu_header;
        default: ingress;
    }
}


parser parse_cpu_header {
    extract(cpu_header);
    return ingress;
}


#endif