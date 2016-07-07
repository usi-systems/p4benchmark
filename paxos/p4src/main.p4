#include "header.p4"
#include "parser.p4"

/*
 * counter paxos_inst {
 *     type : packets;
 *     instance_count : 1;
 *     min_width : INST_SIZE;
 * }
 */

register acceptor_id {
    width: ACPTID_SIZE;
    instance_count : 1; 
}

register acceptors {
    width: NUM_ACCEPTORS;           // The number of acceptors in configuration
    instance_count : INST_COUNT; 
}

register prepare_quorum {
    width: NUM_ACCEPTORS;           // Count the number of PAXOS_1B messages
    instance_count : INST_COUNT; 
}

register phase2_acceptors {
    width: NUM_ACCEPTORS;           // The number of acceptors in configuration
    instance_count : INST_COUNT; 
}

register accept_quorum {
    width: NUM_ACCEPTORS;           // Count the number of PAXOS_2B messages
    instance_count : INST_COUNT; 
}


register ballots_register {
    width : BALLOT_SIZE;
    instance_count : INST_COUNT;
}

register vballots_register {
    width : BALLOT_SIZE;
    instance_count : INST_COUNT;
}

register pxvalue {
    width : PXVALUE_SIZE;
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


action _nop() {

}

action _drop() {
    drop();
}

action read_ballot() {
    register_read(local_metadata.ballot, ballots_register, paxos.inst); 
    modify_field(local_metadata.set_drop, 1);
}

table ballot_state {
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
    register_read(paxos1b.pxvalue, pxvalue, paxos.inst);
    register_read(paxos1b.acptid, acceptor_id, 0);
    modify_field(udp.checksum, 0);
    modify_field(local_metadata.set_drop, 0);
}


action handle_phase2a() {
    register_write(ballots_register, paxos.inst, paxos2a.ballot);
    register_write(vballots_register, paxos.inst, paxos2a.ballot);
    register_write(pxvalue, paxos.inst, paxos2a.pxvalue);
    remove_header(paxos2a);
    add_header(paxos2b);
    modify_field(paxos.msgtype, PAXOS_2B);
    modify_field(paxos2b.ballot, paxos2a.ballot);
    modify_field(paxos2b.pxvalue, paxos2a.pxvalue);
    register_read(paxos2b.acptid, acceptor_id, 0);
    modify_field(udp.checksum, 0);
    modify_field(local_metadata.set_drop, 0);
}


table drop_tbl {
    reads {
        local_metadata.set_drop : exact;
    }
    actions { _drop; _nop; }
    size : 2;
}


table paxos_acceptor {
    reads {
        local_metadata.msgtype : exact;
    }
    actions {
        handle_phase1a;
        handle_phase2a;
        _nop;
    }
    size : 4;
}


action handle_phase1b() {
    register_write(acceptors, paxos.inst, local_metadata.acceptors | ( 1 << local_metadata.packet_acptid));
    register_write(prepare_quorum, paxos.inst, local_metadata.count + 1);
    modify_field(local_metadata.count, local_metadata.count + 1);
}

action handle_phase2b() {
    register_write(phase2_acceptors, paxos.inst, local_metadata.acceptors | ( 1 << local_metadata.packet_acptid));
    register_write(accept_quorum, paxos.inst, local_metadata.count + 1);
    modify_field(local_metadata.count, local_metadata.count + 1);
}

table paxos_proposer {
    reads {
        local_metadata.msgtype : exact;
    }
    actions {
        handle_phase1b;
        handle_phase2b;
        _nop;
    }
    size : 4;
}


action send_accept() {
    remove_header(paxos1b);
    modify_field(paxos.msgtype, PAXOS_2A);
    add_header(paxos2a);
    modify_field(paxos2a.ballot, local_metadata.ballot);
    register_read(paxos2a.pxvalue, pxvalue, paxos.inst);
    modify_field(udp.checksum, 0);
    modify_field(local_metadata.set_drop, 0);
}


action send_deliver() {
    remove_header(paxos2b);
    modify_field(paxos.msgtype, PAXOS_DELIVER);
    add_header(paxos_deliver);
    modify_field(paxos_deliver.pxvalue, paxos2b.pxvalue);
    modify_field(udp.checksum, 0);
    modify_field(local_metadata.set_drop, 0);
}

table next_phase {
    reads {
        local_metadata.msgtype : exact;
    }
    actions {
        send_accept;
        send_deliver;
        _nop;
    }
    size : 4;
}


action update_prepare_state() {
    register_write(vballots_register, paxos.inst, local_metadata.packet_vballot);
    register_write(pxvalue, paxos.inst, paxos1b.pxvalue);
}

table prepare_state {
    actions {
        update_prepare_state;
    }
    size : 1;
}

action load_prepare_state() {
    register_read(local_metadata.highest_accepted_ballot, vballots_register, paxos.inst); 
    register_read(local_metadata.acceptors, acceptors, paxos.inst); 
    register_read(local_metadata.count, prepare_quorum, paxos.inst); 
}

action load_accept_state() {
    register_read(local_metadata.acceptors, phase2_acceptors, paxos.inst); 
    register_read(local_metadata.count, accept_quorum, paxos.inst); 
}

table proposer_state {
    reads {
        local_metadata.msgtype : exact;
    }
    actions {
        load_prepare_state;
        load_accept_state;
        _nop;
    }
    size : 4;
}

control proposer_ctrl {
    apply(proposer_state);
    if ( ((1 << local_metadata.packet_acptid) & local_metadata.acceptors) == 0) {
        apply(paxos_proposer) {
            handle_phase1b {
                if (local_metadata.highest_accepted_ballot < local_metadata.packet_vballot) {
                    apply(prepare_state);
                }
            }
        }
        if (local_metadata.count == QUORUM_SIZE) {
            apply(next_phase);
        } 
    }
}

control ingress {
    if (valid (ipv4))
        apply(forward_tbl);

    if (valid (paxos)) {
        apply(ballot_state);
        if (local_metadata.ballot <= local_metadata.packet_ballot) {
            apply(paxos_acceptor) {
                default {
                    if (local_metadata.ballot == local_metadata.packet_ballot) {
                        proposer_ctrl();   
                    }
                }
            }
        } 
    }
    apply(drop_tbl);
}