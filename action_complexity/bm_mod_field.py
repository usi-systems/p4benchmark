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

    action_name = 'mod_headers'
    program += benchmark_modify_header_overhead(action_name, nb_operations)

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
    get_packetmod_pcap(nb_headers, nb_fields, 'mod', out_dir)

    return True
