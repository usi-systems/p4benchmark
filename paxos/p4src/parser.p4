header ethernet_t ethernet;
header ipv4_t ipv4;
header udp_t udp;
header paxos_t paxos;
header phase1a_t paxos1a;
header phase1b_t paxos1b;
header phase2a_t paxos2a;
header phase2b_t paxos2b;


metadata local_metadata_t local_metadata;

parser start {
    return parse_ethernet;
}

parser parse_ethernet {
    extract(ethernet);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4; 
        default : ingress;
    }
}

parser parse_ipv4 {
    extract(ipv4);
    return select(latest.protocol) {
        UDP_PROTOCOL : parse_udp;
        default : ingress;
    }
}

parser parse_udp {
    extract(udp);
    return select(latest.dstPort) {
        PAXOS_PROTOCOL : parse_paxos;
        default: ingress;
    }
}

parser parse_paxos {
    extract(paxos);
    set_metadata(local_metadata.msgtype, latest.msgtype);
    return select(latest.msgtype) {
        PAXOS_1A : parse_1a;
        PAXOS_1B : parse_1b;
        PAXOS_2A : parse_2a;
        PAXOS_2B : parse_2b;
        default : ingress;
    }
}

parser parse_1a {
    extract(paxos1a);
    set_metadata(local_metadata.packet_ballot, latest.ballot);
    return ingress;
}

parser parse_1b {
    extract(paxos1b);
    set_metadata(local_metadata.packet_ballot, latest.ballot);
    return ingress;
}

parser parse_2a {
    extract(paxos2a);
    set_metadata(local_metadata.packet_ballot, latest.ballot);
    return ingress;
}

parser parse_2b {
    extract(paxos2b);
    set_metadata(local_metadata.packet_ballot, latest.ballot);
    return ingress;
}
