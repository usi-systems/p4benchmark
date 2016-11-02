import os
from subprocess import call
from pkg_resources import resource_filename
from p4gen.genpcap import get_set_field_pcap
from p4gen.genpcap import set_custom_field_pcap
from p4gen import copy_scripts
from parsing.bm_parser import add_headers_and_parsers
from p4gen.p4template import *

modifications = {
    0 : 'ipv4.diffserv',
    1 : 'ipv4.identification',
    2 : 'ipv4.ttl',
    3 : 'ipv4.hdrChecksum',
    4 : 'udp.srcPort',
    5 : 'udp.checksum',
}

modifications_pisces = {
    0 : 'ipv4_diffserv',
    1 : 'ipv4_identification',
    2 : 'ipv4_ttl',
    3 : 'ipv4_hdrChecksum',
    4 : 'udp_srcPort',
    5 : 'udp_checksum',
}

def write_to_ip_and_udp(action_name, nb_operation):
    instruction_set =''
    for i in range(nb_operation):
        instruction_set += '\tmodify_field({0}, {1});\n'.format( modifications[i%len(modifications)], i)
    return add_compound_action(action_name, '', instruction_set)

def write_to_custom_header(action_name, nb_operation):
    instruction_set =''
    for i in range(nb_operation):
        instruction_set += '\tmodify_field(header_0.field_{0}, 1);\n'.format(i)
    return add_compound_action(action_name, '', instruction_set)

def generate_pisces_command_mod_ip_udp(nb_operation, out_dir, checksum=False):
    rules = add_pisces_forwarding_rule()
    actions = ''
    for i in range(nb_operation):
        # match = 'udp_dstPort=0x9091'
        match = ''
        actions += 'set_field:{0}->{1},'.format(i, modifications_pisces[i%len(modifications_pisces)])
    if checksum:
        ip_checksum = 'calc_fields_update(ipv4_hdrChecksum,csum16,fields:ipv4_version_ihl,ipv4_diffserv,ipv4_totalLen,ipv4_identification,ipv4_flags_fragOffset,ipv4_ttl,ipv4_protocol,ipv4_srcAddr,ipv4_dstAddr),'
        actions += ip_checksum
        udp_checksum = "calc_fields_update(udp_checksum,csum16,fields:ipv4_srcAddr,ipv4_dstAddr,0x8'0,ipv4_protocol,udp_length_,udp_srcPort,udp_dstPort,udp_length_,payload),"
        actions += udp_checksum
    actions += 'deparse,output:NXM_NX_REG0[]'
    rules += add_openflow_rule(1, 32768, match, actions)
    with open ('%s/pisces_rules.txt' % out_dir, 'w') as out:
        out.write(rules)

def generate_pisces_command(nb_operation, out_dir, checksum=False):
    rules = add_pisces_forwarding_rule()
    match = 'ethernet_dstAddr=0x0708090A0B0C'
    action = 'set_field:2->reg0,resubmit(,1)'
    rules += add_openflow_rule(0, 32768, match, action)

    actions = ''
    match = 'ptp_reserved2=0x1'
    for i in range(nb_operation):
        actions += 'set_field:{0}->header_0_field_{1},'.format(i+1, i)
    actions += 'deparse,output:NXM_NX_REG0[]'
    rules += add_openflow_rule(1, 32768, match, actions)
    with open ('%s/pisces_rules.txt' % out_dir, 'w') as out:
        out.write(rules)

def benchmark_field_write(nb_operations, do_checksum=False):
    """
    This method generate the P4 program to benchmark packet modification

    :param nb_operations: the number of Set-Field actions
    :type nb_operations: int
    :returns: bool -- True if there is no error

    """
    out_dir = 'output'
    if not os.path.exists(out_dir):
       os.makedirs(out_dir)

    fwd_tbl = 'forward_table'
    nb_headers = 1
    program  = add_headers_and_parsers(nb_headers, nb_operations)
    program += nop_action()
    program += forward_table()

    action_name = 'mod_headers'
    program += write_to_custom_header(action_name, nb_operations)

    table_name = 'test_tbl'
    match = 'ptp.reserved2 : exact;'
    actions = '\t\t_nop;\n\t\t{0};'.format(action_name)
    program += add_table(table_name, match, actions, 4)


    program += control(fwd_tbl, apply_table(table_name))

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands = add_default_rule(table_name, '_nop')
    # commands += add_rule(table_name, action_name, 319)
    commands += add_default_rule(table_name, action_name)
    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)
    set_custom_field_pcap(nb_operations, out_dir, packet_size=256)
    generate_pisces_command(nb_operations, out_dir, do_checksum)
    return True


def benchmark_field_write_to_ip_udp(nb_operations, do_checksum=False):
    """
    This method generate the P4 program to benchmark packet modification

    :param nb_operations: the number of Set-Field actions
    :type nb_operations: int
    :returns: bool -- True if there is no error

    """
    out_dir = 'output'
    if not os.path.exists(out_dir):
       os.makedirs(out_dir)

    program = p4_define() + ethernet() + ipv4(checksum=do_checksum) + tcp() + \
            add_udp_header() + add_udp_parser(checksum=do_checksum) + \
            forward_table() + nop_action()

    fwd_tbl = 'forward_table'

    action_name = 'mod_headers'
    program += write_to_ip_and_udp(action_name, nb_operations)

    table_name = 'test_tbl'
    match = 'udp.dstPort : exact;'
    actions = '\t\t_nop;\n\t\t{0};'.format(action_name)
    program += add_table(table_name, match, actions, 4)


    program += control(fwd_tbl, apply_table(table_name))

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands = add_default_rule(table_name, '_nop')
    # commands += add_rule(table_name, action_name, 319)
    commands += add_default_rule(table_name, action_name)
    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)
    get_set_field_pcap(out_dir, packet_size=256)
    generate_pisces_command_mod_ip_udp(nb_operations, out_dir, do_checksum)

    return True
