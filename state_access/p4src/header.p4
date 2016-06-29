#ifndef _HEADERS_P4_
#define _HEADERS_P4_


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


header_type udp_t {
    fields {
        srcPort : 16;
        dstPort : 16;
        length_ : 16;
        checksum : 16;
    }
}


header_type paxos_t {
    fields {
        px_type : 16;
    }
}


header_type accept_t {
    fields {
        inst : 32;
        px_value : 32;
    }
}


header_type retrieve_t {
    fields {
        from : 32;
        to : 32;
    }
}


header_type local_metadata_t {
    fields {
        index : 32;
        from : 32;
        to : 32;
    }
}


#endif