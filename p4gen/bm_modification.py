import os
from subprocess import call

from p4template import *
from bm_parser import add_headers_and_parsers

def benchmark_modification(args):
    program_name = 'output'
    if not os.path.exists(program_name):
       os.makedirs(program_name)

    fwd_tbl = 'forward_table'

    program  = add_headers_and_parsers(args.headers, args.fields)

    program += forward_table()


    instruction_set =''
    for i in range(args.headers):
        instruction_set += '\tadd_header(header_%d);\n' % i 

    action_name = 'add_headers'
    program += add_compound_action(action_name, '', instruction_set)

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
