#!/usr/bin/env python

import sys, os
import argparse
from subprocess import call
from string import Template

def read_template(filename, binding={}):
    with open (filename, "r") as code_template:
        src = Template(code_template.read())
    return src.substitute(binding)

def p4_define():
    p4_define = read_template('template/define.txt')
    return p4_define

def ethernet():
    ethernet_hdr = read_template('template/headers/ethernet.txt')
    parse_eth = read_template('template/parsers/parse_ethernet.txt')
    return (ethernet_hdr + parse_eth)

def ipv4():
    ipv4_hdr = read_template('template/headers/ipv4.txt')
    parse_ipv4 = read_template('template/parsers/parse_ipv4.txt')
    return (ipv4_hdr + parse_ipv4)

def tcp():
    tcp_hdr = read_template('template/headers/tcp.txt')
    parse_tcp = read_template('template/parsers/parse_tcp.txt')
    return (tcp_hdr + parse_tcp)

def udp():
    udp_hdr = read_template('template/headers/udp.txt')
    parse_udp = read_template('template/parsers/parse_udp.txt')
    return (udp_hdr + parse_udp)

def nop_action():
    return read_template('template/actions/nop.txt')

def forward_table():
    d = { 'tbl_name': 'forward_table' }
    return read_template('template/tables/forward_table.txt', d)

def nop_table(tbl_name):
    return read_template('template/tables/nop_table.txt', {'tbl_name': tbl_name})

def apply_table(tbl_name):
    return read_template('template/controls/apply_table.txt', {'tbl_name': tbl_name})

def control(fwd_tbl, applies):
    d = { 'fwd_tbl' : fwd_tbl, 'applies': applies }
    return read_template('template/controls/ingress.txt', d)

def cli_commands(fwd_tbl, ):
    return read_template('template/commands/forward.txt', { 'fwd_tbl' : fwd_tbl})

def default_nop(tbl_name):
    return read_template('template/commands/default_nop.txt', {'tbl_name': tbl_name})

def generate_programs(args):
    program_name = 'parser'
    if not os.path.exists(program_name):
       os.makedirs(program_name)

    fwd_tbl = 'forward_table'

    program = p4_define() + ethernet() + ipv4() + tcp() + udp() + \
                forward_table() + nop_action()

    applies = ''
    commands = ''
    for i in range(args.tables):
        tbl_name = 'table_%d' % i
        program += nop_table(tbl_name)
        applies += apply_table(tbl_name) + '\t'
        commands += default_nop(tbl_name)

    program += control(fwd_tbl, applies)

    with open ('%s/main.p4' % program_name, 'w') as out:
        out.write(program)

    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % program_name, 'w') as out:
        out.write(commands)

    call(['cp', 'template/run_switch.sh', program_name])


def main():
    parser = argparse.ArgumentParser(description='A programs that generate a set'
                            ' of P4 programs')
    parser.add_argument("-p", "--parser", default=False, action="store_true",
                            help="parser benchmark")
    parser.add_argument("-t", "--tables", default=1, type=int, help="pipeline benchmark")
    parser.add_argument("-v", "--vlan", default=False, action='store_true',
                        help="send a VLAN tag packet")

    args = parser.parse_args()

    if args.parser:
        generate_programs(args)
    else:
        parser.print_help()

if __name__=='__main__':
    main()