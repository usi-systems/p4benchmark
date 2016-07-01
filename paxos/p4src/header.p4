#define ETHERTYPE_IPV4 0x0800
#define UDP_PROTOCOL 0x11
#define PAXOS_PROTOCOL 0x8888


#define PAXOS_1A 0
#define PAXOS_1B 1
#define PAXOS_2A 2
#define PAXOS_2B 3

#define MSGTYPE_SIZE 16
#define INST_SIZE 32
#define BALLOT_SIZE 16
#define ACPTID_SIZE 16
#define INST_COUNT 10
#define CHECKSUM_SIZE 32


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

header_type udp_t {
    fields {
        srcPort : 16;
        dstPort : 16;
        length_ : 16;
        checksum : 16;
    }
}


header_type local_metadata_t {
    fields {
        msgtype : MSGTYPE_SIZE;
        ballot : BALLOT_SIZE;
        packet_ballot : BALLOT_SIZE;
        checksum : 32;
    }
}

// Headers for Paxos

header_type paxos_t {
    fields {
        msgtype  : MSGTYPE_SIZE;
        inst   : INST_SIZE;
    }
}

header_type phase1a_t {
    fields {
        ballot : BALLOT_SIZE;
    }
}

header_type phase1b_t {
    fields {
        ballot   : BALLOT_SIZE;
        vballot  : BALLOT_SIZE;
        acptid   : ACPTID_SIZE;
        val_cksm : CHECKSUM_SIZE;
    }
}

header_type phase2a_t {
    fields {
        ballot   : BALLOT_SIZE;
        val_cksm : CHECKSUM_SIZE;
    }
}

header_type phase2b_t {
    fields {
        ballot   : BALLOT_SIZE;
        acptid   : ACPTID_SIZE;
        val_cksm : CHECKSUM_SIZE;
    }
}
