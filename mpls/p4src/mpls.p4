// Push one or more labels from the top of the label stack
action push_label(outgoing_label) {
    push(label_stack, 1);
    modify_field(label_stack[0].label, outgoing_label);
    modify_field(ipv4.ttl, ipv4.ttl-1);
    modify_field(label_stack[0].ttl, ipv4.ttl);
}

// Swap two labels
action swap_label(outgoing_label) {
    modify_field(label_stack[0].label, outgoing_label);
}

action set_next_hop(next_hop) {
    modify_field(ipv4.dstAddr, next_hop);
    modify_field(ipv4.ttl, ipv4.ttl-1);
}

action ip_to_label(label, next_hop) {
    push_label(label);
    set_next_hop(next_hop);
    modify_field(eth.dl_type, MPLS_PROTOCOL);
    modify_field(label_stack[0].bos, 1);
}

action ip_to_ip(next_hop) {
    set_next_hop(next_hop);
}

action label_to_label(outgoing_label, next_hop) {
    swap_label(outgoing_label);
    set_next_hop(next_hop);
}


action label_to_ip(next_hop) {
    pop(label_stack, 1);
    set_next_hop(next_hop);
}

action untag(next_hop) {
    modify_field(ipv4.ttl, label_stack[0].ttl);
    pop(label_stack, STACK_DEPTH);
    modify_field(eth.dl_type, IP_PROTOCOL);
    set_next_hop(next_hop);
}

action aggregate() {
    // Go to IPFIB, IP lookup
}

table LFIB {
    reads {
        label_stack[0].label : exact;
    }
    actions {
        label_to_label;
        label_to_ip;
        untag;
        aggregate;
        push_label;
        _drop;
    }
}


table IPFIB {
    reads {
        ipv4.dstAddr : lpm;
    }
    actions {
        ip_to_label;
        ip_to_ip;
        _drop;
    }
}