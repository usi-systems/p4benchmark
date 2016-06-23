header_type ldp_t {
    fields {
        version : 16;
        pdu_length : 16;
        lsr_id : 32;
        lsi : 16;
    }
}

header_type tlv_t {
    fields {
        unknown : 1;
        forward : 1;
        msg_type : 14;
    }
}

header_type keep_alive_t {
    fields {
        msg_length : 16;
        msg_id : 32;
    }
}

header_type address_message_t {
    fields {
        msg_length : 16;
        msg_id : 32;
    }
}

header_type address_list_t {
    fields {
        msg_length : 16;
        address_family : 16;
    }
}

header_type address_t {
    fields {
        ip : 32;
    }
}

header_type mpls_meta_t {
    fields {
        msg_length : 16;
        addr_count : 16;
    }
}