
header_type ethernet_t {
    fields {
        dl_dst : 48;
        dl_src : 48;
        dl_type : 16;
    }
}

header_type vlan_t {
    fields {
        pcp : 3;
        dei : 1;
        vid : 12;
        dl_type : 16;
    }
}

parser start {
    return parse_ethernet;
}

header ethernet_t eth;
header vlan_t vlan;

#define IPV4_PROTOCOL 0x800
#define VLAN_PROTOCOL 0x8100

parser parse_ethernet {
    extract(eth);
    return select(latest.dl_type) {
        VLAN_PROTOCOL : parse_vlan;
        default : ingress;
    }
}

parser parse_vlan {
    extract(vlan);
    return ingress;
}

action tag_vlan(vid) {
    modify_field(eth.dl_type, VLAN_PROTOCOL);
    add_header(vlan);
    modify_field(vlan.vid, vid);
    modify_field(vlan.dl_type, IPV4_PROTOCOL);
}

action untag_vlan() {
    remove_header(vlan);
    modify_field(eth.dl_type, IPV4_PROTOCOL);
}

action _drop() {
    drop();
}

action _nop() {

}

action forward(port) {
    modify_field(standard_metadata.egress_spec, port);
}

table vlan_tbl {
    reads {
        standard_metadata.ingress_port : exact;
    }
    actions {
        tag_vlan;
        untag_vlan;
        _nop;
    }
}

table forward_tbl {
    reads {
        eth.dl_dst : exact;
    } actions {
        forward;
        _drop;
    }
}
control ingress {
    apply(vlan_tbl);
    apply(forward_tbl);
}