import os
from subprocess import call

from p4template import *

def add_headers_and_parsers(nb_headers, nb_fields):
    """
    This method adds Ethernet, IPv4, TCP, UDP, and a number of generic headers
    which follow the UDP header. The UDP destination port 0x9091 is used to
    identify the generic header

    :param nb_headers: the number of generic headers included in the program
    :type nb_headers: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type tbl_size: int
    :returns: str -- the header and parser definition

    """
    program = p4_define() + ethernet() + ipv4() + tcp()
    program += udp(select_case(0x9091, 'parse_header_0'))

    field_dec = ''
    for i in range(nb_fields):
        field_dec += add_header_field('field_%d' % i, 16)

    for i in range(nb_headers):
        header_type_name = 'header_%d_t' % i
        header_name = 'header_%d' % i
        parser_state_name = 'parse_header_%d' % i
        if (i < (nb_headers - 1)):
            next_state  = select_case(0, 'ingress')
            next_state += select_case('default', 'parse_header_%d' % (i + 1))
        else:
            next_state = select_case('default', 'ingress')
        program += add_header(header_type_name, field_dec)
        program += add_parser(header_type_name, header_name, parser_state_name,
                                'field_0', next_state)
    return program


def benchmark_parser(args):
    program_name = 'output'
    if not os.path.exists(program_name):
       os.makedirs(program_name)

    fwd_tbl = 'forward_table'

    program  = add_headers_and_parsers(args.headers, args.fields)
    program += forward_table()
    program += control(fwd_tbl, '')

    with open ('%s/main.p4' % program_name, 'w') as out:
        out.write(program)

    commands = cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % program_name, 'w') as out:
        out.write(commands)

    call(['cp', 'template/run_switch.sh', program_name])
