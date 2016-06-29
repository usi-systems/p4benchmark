#ifndef _PARSER_P4_
#define _PARSER_P4_


header ethernet_t eth;
header ipv4_t ipv4;
header udp_t udp;


parser start {
    return parse_ethernet;
}

#define ETHERTYPE_IPV4         0x0800

parser parse_ethernet {
    extract(eth);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4;
        default : ingress;
    }
}

#define IP_PROTOCOLS_UDP               17

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
        IP_PROTOCOLS_UDP : parse_udp;
        default: ingress;
    }
}


#define PAXOS_PORT  0x8888

parser parse_udp {
    extract(udp);
    return select (latest.dstPort) {
        PAXOS_PORT : parse_paxos;
        default : ingress;
    }
}


#define VALUE_TYPE      0x2
#define RETRIEVE_TYPE   0x6

header paxos_t paxos;

metadata local_metadata_t local_metadata;

parser parse_paxos {
    extract(paxos);
    return select(latest.px_type) {
        VALUE_TYPE : parse_value;
        RETRIEVE_TYPE : parse_retrieve;
        default : ingress;
    }
}

header accept_t paxos_value;

parser parse_value {
    extract(paxos_value);
    set_metadata(local_metadata.index, latest.inst);
    return ingress;
}

header retrieve_t retrieve;

parser parse_retrieve {
    extract(retrieve);
    return ingress;
}


#endif