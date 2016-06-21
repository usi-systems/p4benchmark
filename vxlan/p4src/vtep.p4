
header_type ethernet_t {
    fields {
        dstAddr : 48;
        srcAddr : 48;
        etherType : 16;
    }
}


header_type ipv4_t {
    fields {
        version : 4;
        ihl : 4;
        diffserv : 8;
        totalLen : 16;
        identification : 16;
        flags : 3;
        fragOffset : 13;
        ttl : 8;
        protocol : 8;
        hdrChecksum : 16;
        srcAddr : 32;
        dstAddr : 32;
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

calculated_field outer_ipv4.hdrChecksum  {
    update ipv4_checksum if (ipv4.ihl == 5);
}


header_type udp_t {
    fields {
        srcPort : 16;
        dstPort :16;
        len : 16;
        checksum : 16;
    }
}


header_type vxlan_t {
    fields {
        flags : 16;
        group_policy_id : 16;
        vni : 24;
        reserved2 : 8;
    }
}

header ethernet_t eth;
header ipv4_t ipv4;
header udp_t udp;
header vxlan_t vxlan;

header ethernet_t outer_eth;
header ipv4_t outer_ipv4;
header udp_t outer_udp;
header vxlan_t outer_vxlan;


#define VXLAN_PORT  4789

parser start {
    return select(current(288,16)) {
        VXLAN_PORT : parse_outer_eth;
        default : parse_eth;
    }
}

#define ETHERTYPE_IPV4  0x0800

parser parse_outer_eth {
    extract(outer_eth);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_outer_ipv4;
        default : ingress;
    }
}

parser parse_eth {
    extract(eth);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4;
        default : ingress;
    }
}

#define IP_PROTOCOLS_UDP  17

parser parse_outer_ipv4 {
    extract(outer_ipv4);
    return select(latest.protocol) {
        IP_PROTOCOLS_UDP : parse_outer_udp;
        default : ingress;
    }
}


parser parse_ipv4 {
    extract(ipv4);
    return select(latest.protocol) {
        IP_PROTOCOLS_UDP : parse_udp;
        default : ingress;
    }
}


parser parse_outer_udp {
    extract(outer_udp);
    return select(latest.dstPort) {
        VXLAN_PORT : parse_outer_vxlan;
        default : ingress;
    }
}


parser parse_udp {
    extract(udp);
    return select(latest.dstPort) {
        VXLAN_PORT : parse_vxlan;
        default : ingress;
    }
}

parser parse_outer_vxlan {
    extract(outer_vxlan);
    return select(latest.flags) {
        default :parse_eth;
    }
}

parser parse_vxlan {
    extract(vxlan);
    return ingress;
}

action _nop() {

}



action encap_vxlan(vni, srcmac, dstmac, srcip, dstip) {
    add_header(outer_eth);
    modify_field(outer_eth.srcAddr, dstmac);
    modify_field(outer_eth.dstAddr, srcmac);
    modify_field(outer_eth.etherType, ETHERTYPE_IPV4);

    copy_header(outer_ipv4, ipv4);
    modify_field(outer_ipv4.totalLen, ipv4.totalLen + 50);
    modify_field(outer_ipv4.srcAddr, srcip);
    modify_field(outer_ipv4.dstAddr, dstip);


    add_header(outer_udp);
    modify_field(outer_udp.srcPort, ipv4.hdrChecksum);
    modify_field(outer_udp.dstPort, VXLAN_PORT);
    modify_field(outer_udp.len, outer_ipv4.totalLen - 20);

    add_header(outer_vxlan);
    modify_field(outer_vxlan.flags, ETHERTYPE_IPV4);
    modify_field(outer_vxlan.vni, vni);
}


table mac_to_vtep {
    reads {
        eth.dstAddr : exact;
    } actions {
        encap_vxlan;
        _nop;
    }
}

action _drop() {
    drop();
}

action forward(port) {
    modify_field(standard_metadata.egress_spec, port);
}

table forwarding {
    reads {
        eth.dstAddr : exact;
    } actions {
        forward;
        _drop;
    }
}


control ingress {
    apply(mac_to_vtep);
    apply(forwarding);
}


control egress {
}







