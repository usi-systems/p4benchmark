#ifndef _HEADER_P4_
#define _HEADER_P4_

header_type ethernet_t {
    fields {
        dl_dst : 48;
        dl_src : 48;
        dl_type : 16;
    }
}


header_type mpls_label_t {
    fields {
        label   : 20;
        exp     : 3;
        bos     : 1;
        ttl     : 8;
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


header_type ingress_metadata_t {
    fields {
        count : 32;
    }
}

#endif