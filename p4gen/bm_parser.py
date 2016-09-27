import os
from subprocess import call

from p4template import *

def benchmark_parser(args):
    program_name = 'output'
    if not os.path.exists(program_name):
       os.makedirs(program_name)

    fwd_tbl = 'forward_table'

    # Generic headers are added after UDP header.
    # 0x9091 is used to identify the generic header
    program = p4_define() + ethernet() + ipv4() + tcp() + udp('0x9091 : parse_header_0;')

    applies = ''
    commands = ''
    field_dec = ''
    for i in range(args.fields):
        if (i < args.fields - 1):
            field_dec += 'dummy_%d: 16;\n\t\t' % i
        else:
            field_dec += 'dummy_%d: 16;' % i

    for i in range(args.headers):
        header_type_name = 'header_%d_t' % i
        header_name = 'header_%d' % i
        parser_state_name = 'parse_header_%d' % i
        if (i < (args.headers - 1)):
            next_state = 'parse_header_%d' % (i + 1)
        else:
            next_state = 'ingress'
        program += new_header(header_type_name, field_dec)
        program += new_parser(header_type_name, header_name, parser_state_name,
                                next_state)

    program += forward_table()
    program += control(fwd_tbl, applies)

    with open ('%s/main.p4' % program_name, 'w') as out:
        out.write(program)

    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % program_name, 'w') as out:
        out.write(commands)

    call(['cp', 'template/run_switch.sh', program_name])
