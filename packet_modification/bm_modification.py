import os
from subprocess import call
from pkg_resources import resource_filename
from parsing.bm_parser import add_headers_and_parsers
from p4gen.genpcap import get_packetmod_pcap
from p4gen import copy_scripts
from p4gen.p4template import *

def generate_pisces_command(nb_headers, out_dir):
    rules = add_pisces_forwarding_rule()
    actions = ''
    for i in range(nb_headers-1):
        actions += 'set_field:1->header_{0}_field_0,'.format(i)
    actions += 'set_field:0x9091->udp_dstPort,deparse,output:NXM_NX_REG0[]'
    rules += add_openflow_rule(1, 12345, actions)

    with open ('%s/pisces_rules.txt' % out_dir, 'w') as out:
        out.write(rules)


def benchmark_add_header_overhead(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\tadd_header(header_%d);\n' % i
        # TODO: uncomment if headers are not added in deparser
        # if i < nb_header - 1:
        #     instruction_set += '\tmodify_field(header_%d.field_0, 1);\n' % i

    # Change udp port to include generic headers in deparser
    # TODO: parameterize the protocol number for the generic header
    instruction_set += '\tmodify_field(udp.dstPort, 0x9091);'
    return add_compound_action(action_name, '', instruction_set)

def benchmark_remove_header_overhead(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\tremove_header(header_%d);\n' % i

    # Change udp port to skip generic headers in deparser
    instruction_set += '\tmodify_field(udp.dstPort, 12345);'
    return add_compound_action(action_name, '', instruction_set)

def benchmark_modify_header_overhead(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\tmodify_field(header_{0}.field_0, ' \
                            'header_{0}.field_0 + 1);\n'.format(i)
    return add_compound_action(action_name, '', instruction_set)


def benchmark_modification(nb_headers, nb_fields, mod_type):
    """
    This method generate the P4 program to benchmark packet modification

    :param nb_headers: the number of generic headers included in the program
    :type nb_headers: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type tbl_size: int
    :param nb_fields: modification type ['add', 'rm', 'mod']
    :type tbl_size: str
    :returns: bool -- True if there is no error

    """
    out_dir = 'output'
    if not os.path.exists(out_dir):
       os.makedirs(out_dir)

    fwd_tbl = 'forward_table'

    program  = add_headers_and_parsers(nb_headers, nb_fields)

    if mod_type == 'add':
        action_name = 'add_headers'
        program += benchmark_add_header_overhead(action_name, nb_headers)
    elif mod_type == 'rm':
        action_name = 'remove_headers'
        program += benchmark_remove_header_overhead(action_name, nb_headers)
    elif mod_type == 'mod':
        action_name = 'mod_headers'
        program += benchmark_modify_header_overhead(action_name, nb_headers)

    program += forward_table()

    table_name = 'test_tbl'
    program += add_table_no_match(table_name, '\t\t{0};'.format(action_name))


    program += control(fwd_tbl, apply_table(table_name))

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands = add_default_rule(table_name, action_name)
    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)
    get_packetmod_pcap(nb_headers, nb_fields, mod_type, out_dir)
    generate_pisces_command(nb_headers, out_dir)

    return True
