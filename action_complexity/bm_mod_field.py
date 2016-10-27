import os
from subprocess import call
from pkg_resources import resource_filename
from parsing.bm_parser import add_headers_and_parsers
from p4gen.genpcap import get_packetmod_pcap
from p4gen import copy_scripts
from p4gen.p4template import *

def benchmark_modify_header_overhead(action_name, nb_operation):
    instruction_set =''
    for i in range(nb_operation):
        instruction_set += '\tmodify_field(header_0.field_{0}, 1);\n'.format(i)
    return add_compound_action(action_name, '', instruction_set)

def generate_pisces_command(nb_operation, out_dir):
    rules = add_pisces_forwarding_rule()
    actions = ''
    for i in range(nb_operation):
        match = 'udp_dstPort=0x9091'
        actions += 'set_field:1->header_0_field_{0},'.format(i)
    actions += 'deparse,output:NXM_NX_REG0[]'
    rules += add_openflow_rule(1, 12345, match, actions)

    with open ('%s/pisces_rules.txt' % out_dir, 'w') as out:
        out.write(rules)

def benchmark_field_write(nb_operations, nb_fields):
    """
    This method generate the P4 program to benchmark packet modification

    :param nb_operations: the number of generic headers included in the program
    :type nb_operations: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type nb_fields: int
    :returns: bool -- True if there is no error

    """
    out_dir = 'output'
    if not os.path.exists(out_dir):
       os.makedirs(out_dir)

    fwd_tbl = 'forward_table'

    nb_headers = 1
    program  = add_headers_and_parsers(nb_headers, nb_fields)
    program += nop_action()

    action_name = 'mod_headers'
    program += benchmark_modify_header_overhead(action_name, nb_operations)

    program += forward_table()

    table_name = 'test_tbl'
    match = 'udp.dstPort : exact;'
    actions = '\t\t_nop;\n\t\t{0};'.format(action_name)
    program += add_table(table_name, match, actions, 4)


    program += control(fwd_tbl, apply_table(table_name))

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands = add_default_rule(table_name, '_nop')
    commands += add_rule(table_name, action_name, 0x9091)
    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)
    get_packetmod_pcap(nb_headers, nb_fields, 'mod', out_dir)
    generate_pisces_command(nb_operations, out_dir)

    return True
