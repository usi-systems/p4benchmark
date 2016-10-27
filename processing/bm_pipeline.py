import os
from subprocess import call
from pkg_resources import resource_filename
from p4gen.genpcap import get_pipeline_pcap
from p4gen import copy_scripts
from p4gen.p4template import *

def generate_pisces_command(nb_tables, out_dir):
    rules = add_pisces_forwarding_rule()
    actions = ''
    for i in range(nb_tables-1):
        match = ''
        actions = 'resubmit(,{0})'.format(i+2)
        rules += add_openflow_rule(i+1, 32768, match, actions)

    actions = 'deparse,output:NXM_NX_REG0[]'
    rules += add_openflow_rule(nb_tables, 32768, '', actions)

    with open ('%s/pisces_rules.txt' % out_dir, 'w') as out:
        out.write(rules)


def benchmark_pipeline(nb_tables, table_size):
    """
    This method generate the P4 program to benchmark the processing pipeline

    :param nb_tables: the number of tables in the pipeline
    :type nb_tables: str
    :param table_size: the size of each table
    :type table_size: int
    :returns: bool -- True if there is no error

    """

    out_dir = 'output'
    if not os.path.exists(out_dir):
       os.makedirs(out_dir)

    fwd_tbl = 'forward_table'

    program = p4_define() + ethernet() + ipv4() + tcp() + udp() + \
            forward_table() + nop_action()

    applies = ''
    commands = ''
    actions = '_nop;'
    for i in range(nb_tables):
        tbl_name = 'table_%d' % i
        program += add_table_no_match(tbl_name, actions, table_size)
        applies += apply_table(tbl_name) + '\t'
        commands += default_nop(tbl_name)

    program += control(fwd_tbl, applies)

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)

    get_pipeline_pcap(out_dir)
    generate_pisces_command(nb_tables, out_dir)
    return True