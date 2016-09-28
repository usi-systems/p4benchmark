import os
from subprocess import call

from p4template import *
from bm_parser import add_headers_and_parsers

def benchmark_add_header_overhead(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\tadd_header(header_%d);\n' % i

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


def benchmark_modification(args):
    program_name = 'output'
    if not os.path.exists(program_name):
       os.makedirs(program_name)

    fwd_tbl = 'forward_table'

    program  = add_headers_and_parsers(args.headers, args.fields)

    if args.mod_type == 'add':
        action_name = 'add_headers'
        program += benchmark_add_header_overhead(action_name, args.headers)
    elif args.mod_type == 'rm':
        action_name = 'remove_headers'
        program += benchmark_remove_header_overhead(action_name, args.headers)
    elif args.mod_type == 'mod':
        action_name = 'mod_headers'
        program += benchmark_modify_header_overhead(action_name, args.headers)

    program += forward_table()

    table_name = 'test_tbl'
    program += add_table_no_match(table_name, '\t\t{0};'.format(action_name))


    program += control(fwd_tbl, apply_table(table_name))

    with open ('%s/main.p4' % program_name, 'w') as out:
        out.write(program)

    commands = add_default_rule(table_name, action_name)
    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % program_name, 'w') as out:
        out.write(commands)

    call(['cp', 'template/run_switch.sh', program_name])
