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
        dstAddr: 32;
    }
}

header_type tcp_t {
    fields {
        srcPort : 16;
        dstPort : 16;
        seqNo : 32;
        ackNo : 32;
        dataOffset : 4;
        res : 3;
        ecn : 3;
        ctrl : 6;
        window : 16;
        checksum : 16;
        urgentPtr : 16;
    }
}

parser start {
    return parse_ethernet;
}

#define ETHERTYPE_IPV4 0x0800

header ethernet_t ethernet;

parser parse_ethernet {
    extract(ethernet);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4;
        default: ingress;
    }
}

header ipv4_t ipv4;

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
    verify ipv4_checksum;
    update ipv4_checksum;
}

#define IP_PROTOCOLS_TCP 6

parser parse_ipv4 {
    extract(ipv4);
    return select(latest.protocol) {
        IP_PROTOCOLS_TCP : parse_tcp;
        default: ingress;
    }
}

header tcp_t tcp;

parser parse_tcp {
    extract(tcp);
    return ingress;
}


action _drop() {
    drop();
}

header_type routing_metadata_t {
    fields {
        hash_index : 14; // offset into the hash table
    }
}

metadata routing_metadata_t routing_metadata;

#define HASH_OUTPUT_WIDTH 10
#define PREFIX_TABLE_SIZE 1024

field_list l3_hash_fields {
    ipv4.srcAddr;
    ipv4.dstAddr;
    ipv4.protocol;
    tcp.srcPort;
    tcp.dstPort;
}

field_list_calculation tcp_flow {
    input {
        l3_hash_fields;
    }
    algorithm : crc16;
    output_width : HASH_OUTPUT_WIDTH;
}


action hash_to_index(base_index, table_size) {
    modify_field_with_hash_based_offset(routing_metadata.hash_index, base_index,
                                        tcp_flow, table_size);
}

table prefix_to_index {
    reads {
        ipv4.dstAddr : lpm;
    }
    actions {
        _drop;
        hash_to_index;
    }
    size : PREFIX_TABLE_SIZE;
}

action forward(out_port) {
    modify_field(standard_metadata.egress_spec, out_port);
}

table fwd_tbl {
    reads {
        routing_metadata.hash_index : exact;
    }
    actions {
        forward;
    }
}

control ingress {
    if(valid(ipv4) and ipv4.ttl > 0) {
        apply(prefix_to_index);
        apply(fwd_tbl);
    }
}