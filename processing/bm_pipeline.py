import os
from subprocess import call
from pkg_resources import resource_filename
from p4gen.genpcap import get_pipeline_pcap
from p4gen import copy_scripts
from p4gen.p4template import *

def generate_pisces_command(nb_tables, table_size, out_dir):
    rules = add_pisces_forwarding_rule()
    match = 'ethernet_dstAddr=0x0708090A0B0C'
    action = 'set_field:2->reg0,resubmit(,1)'
    rules += add_openflow_rule(0, 32768, match, action)

    actions = ''
    for i in range(nb_tables-1):
        match = 'ethernet_dstAddr=0x0CC47AA32535'
        actions = 'resubmit(,{0})'.format(i+2)
        rules += add_openflow_rule(i+1, 32768, match, actions)
        match = 'ethernet_dstAddr=0x0708090A0B0C'
        actions = 'resubmit(,{0})'.format(i+2)
        rules += add_openflow_rule(i+1, 32768, match, actions)
        for j in range(table_size-2):
            mac_addr = "0x0{0}C47{1}A353{2}".format(j%10, j%7, j%5)
            match = 'ethernet_dstAddr=%s' % mac_addr
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

    # set Minimum table size
    if table_size < 16:
        table_size = 16

    applies = ''
    commands = ''
    match = 'ethernet.dstAddr : exact;'
    params = {1 : ("0C:C4:7A:A3:25:34", 1), 2: ("0C:C4:7A:A3:25:35", 2)}
    action_name = 'forward'
    actions = '%s;' % action_name
    for i in range(nb_tables):
        tbl_name = 'table_%d' % i
        program += add_table(tbl_name, match, actions, table_size)
        applies += apply_table(tbl_name) + '\t'
        commands += add_rule(tbl_name, action_name, params[1][0], params[1][1])
        commands += add_rule(tbl_name, action_name, params[2][0], params[2][1])


    program += control(fwd_tbl, applies)

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)

    get_pipeline_pcap(out_dir)
    generate_pisces_command(nb_tables, table_size, out_dir)
    return True