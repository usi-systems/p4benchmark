#include "header.p4"
#include "parser.p4"

counter paxos_inst {
    type : packets;
    instance_count : 1;
    min_width : INST_SIZE;
}


register acceptor_id {
    width: ACPTID_SIZE;
    instance_count : 1; 
}

register ballots_register {
    width : BALLOT_SIZE;
    instance_count : INST_COUNT;
}

register vballots_register {
    width : BALLOT_SIZE;
    instance_count : INST_COUNT;
}

register value_checksums {
    width : CHECKSUM_SIZE;
    instance_count : INST_COUNT;
}


action forward(port) {
    modify_field(standard_metadata.egress_spec, port);
}

table forward_tbl {
    reads {
        standard_metadata.ingress_port : exact;
    }
    actions {
        forward;
        _drop;
    }
    size : 8;
}


action _drop() {
    drop();
}

action read_ballot() {
    register_read(local_metadata.ballot, ballots_register, paxos.inst); 
}

table ballot_tbl {
    actions { read_ballot; }
    size : 1;
}

action handle_phase1a() {
    register_write(ballots_register, paxos.inst, paxos1a.ballot);
    remove_header(paxos1a);
    add_header(paxos1b);
    modify_field(paxos.msgtype, PAXOS_1B);
    modify_field(paxos1b.ballot, paxos1a.ballot);
    register_read(paxos1b.vballot, vballots_register, paxos.inst);
    register_read(paxos1b.val_cksm, value_checksums, paxos.inst);
    register_read(paxos1b.acptid, acceptor_id, 0);
    modify_field(udp.checksum, 0);
}

action handle_phase2a() {
    register_write(ballots_register, paxos.inst, paxos2a.ballot);
    register_write(vballots_register, paxos.inst, paxos2a.ballot);
    register_write(value_checksums, paxos.inst, paxos2a.val_cksm);
    remove_header(paxos2a);
    add_header(paxos2b);
    modify_field(paxos.msgtype, PAXOS_2B);
    modify_field(paxos2b.ballot, paxos2a.ballot);
    modify_field(paxos2b.val_cksm, paxos2a.val_cksm);
    register_read(paxos2b.acptid, acceptor_id, 0);
    modify_field(udp.checksum, 0);
}

table drop_tbl {
    actions { _drop; }
    size : 1;
}


table paxos_tbl {
    reads {
        local_metadata.msgtype : exact;
    }
    actions {
        handle_phase1a;
        handle_phase2a;
        _drop;
    }
    size : 16;
}


control ingress {
    if (valid (ipv4))
        apply(forward_tbl);

    if (valid (paxos)) {
        apply(ballot_tbl);
        if (local_metadata.ballot <= local_metadata.packet_ballot) {
            apply(paxos_tbl);
        } else {
            apply(drop_tbl);
        }
    }
}