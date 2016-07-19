header ethernet_t ethernet;
header ipv4_t ipv4;
header udp_t udp;

parser start {
    return parse_ethernet;
}

parser parse_ethernet {
    extract(ethernet);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4; 
        default : ingress;
    }
}


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
    update ipv4_checksum if (ipv4.ihl == 5);
}


parser parse_ipv4 {
    extract(ipv4);
    return select(latest.protocol) {
        UDP_PROTOCOL : parse_udp;
        default : ingress;
    }
}

field_list udp_checksum_list {
    ipv4.srcAddr;
    ipv4.dstAddr;
    8'0;
    ipv4.protocol;
    udp.length_;
    udp.srcPort;
    udp.dstPort;
    udp.length_;
    payload;
}

field_list_calculation udp_checksum {
    input {
        udp_checksum_list;
    }
    algorithm : csum16;
    output_width : 16;
}

calculated_field udp.checksum {
    update udp_checksum;
}

parser parse_udp {
    extract(udp);
    return select(latest.dstPort) {
        default: ingress;
    }
}