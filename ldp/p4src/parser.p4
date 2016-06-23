parser start {
    return parse_ethernet;
}

header ethernet_t eth;
header ipv4_t ipv4;
header tcp_t tcp;
header ldp_t ldp[3];
header tlv_t tlv[10];

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

#define LDP_PROTO_PORT 646

parser parse_tcp {
    extract(tcp);
    return select(latest.dstPort) {
        LDP_PROTO_PORT : parse_ldp;
        default : ingress;
    }
}

#define KEEP_ALIVE_MSG 0x201
#define ADDRESS_MSG    0x300
#define ADDRESS_LIST   0x101

parser parse_ldp {
    extract(ldp[next]);
    return parse_tlv;
}

header mpls_meta_t parsed_meta;

parser parse_tlv {
    extract(tlv[next]);
    return select(latest.msg_type) {
        KEEP_ALIVE_MSG : parse_keep_alive;
        ADDRESS_MSG : parse_address_message;
        ADDRESS_LIST : parse_address_list;
        default : ingress;
    }
}

header keep_alive_t keep_alive;

parser parse_keep_alive {
    extract(keep_alive);
    return select(latest.msg_length) {
        0 : ingress;
        default : parse_ldp;
    }
}
 
header address_message_t addr_msg;

parser parse_address_message { 
    extract(addr_msg);
    return select (latest.msg_length) {
        0 : ingress;
        default :parse_tlv;
    }
}


header address_list_t addr_list;
header address_t addresses[4];

#define IPV4_ADDR 1
#define IPV6_ADDR 2

parser parse_address_list {
    extract(addr_list);
    set_metadata(parsed_meta.msg_length, latest.msg_length);
    return select(latest.address_family) {
        IPV4_ADDR : parse_ipv4_addr;
        IPV6_ADDR : parse_ipv6_addr;
        default : ingress;
    }
}

parser parse_ipv4_addr {
    set_metadata(parsed_meta.addr_count, (parsed_meta.msg_length - 2) >> 2);
    return parse_addr;
}

parser parse_addr {
    extract(addresses[next]);
    set_metadata(parsed_meta.addr_count, parsed_meta.addr_count - 1);
    return select(parsed_meta.addr_count) {
        0 : ingress;
        default : parse_addr; 
    }
}


parser parse_ipv6_addr {
    return ingress;
}
