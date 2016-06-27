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