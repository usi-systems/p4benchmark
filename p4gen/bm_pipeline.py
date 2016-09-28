import os
from subprocess import call

from p4template import *

def benchmark_pipeline(args):
    program_name = 'output'
    if not os.path.exists(program_name):
       os.makedirs(program_name)

    fwd_tbl = 'forward_table'

    program = p4_define() + ethernet() + ipv4() + tcp() + udp() + \
            forward_table() + nop_action()

    applies = ''
    commands = ''
    actions = '_nop;'
    for i in range(args.tables):
        tbl_name = 'table_%d' % i
        program += add_table_no_match(tbl_name, actions, args.table_size)
        applies += apply_table(tbl_name) + '\t'
        commands += default_nop(tbl_name)

    program += control(fwd_tbl, applies)

    with open ('%s/main.p4' % program_name, 'w') as out:
        out.write(program)

    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % program_name, 'w') as out:
        out.write(commands)

    call(['cp', 'template/run_switch.sh', program_name])