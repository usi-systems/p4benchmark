import os
from subprocess import call
from pkg_resources import resource_filename
from p4gen.genpcap import get_set_field_pcap
from p4gen import copy_scripts
from p4gen.p4template import *

def benchmark_modify_header_overhead(action_name, nb_operation):
    instruction_set =''
    for i in range(nb_operation):
        instruction_set += '\tmodify_field(udp.srcPort, 319);\n'
    return add_compound_action(action_name, '', instruction_set)

def generate_pisces_command(nb_operation, out_dir):
    rules = add_pisces_forwarding_rule()
    actions = ''
    for i in range(nb_operation):
        # match = 'udp_dstPort=0x9091'
        match = ''
        actions += 'set_field:319->udp_srcPort,'
    actions += 'deparse,output:NXM_NX_REG0[]'
    rules += add_openflow_rule(1, 32768, match, actions)

    with open ('%s/pisces_rules.txt' % out_dir, 'w') as out:
        out.write(rules)

def benchmark_field_write(nb_operations):
    """
    This method generate the P4 program to benchmark packet modification

    :param nb_operations: the number of Set-Field actions
    :type nb_operations: int
    :returns: bool -- True if there is no error

    """
    out_dir = 'output'
    if not os.path.exists(out_dir):
       os.makedirs(out_dir)

    program = p4_define() + ethernet() + ipv4() + tcp() + udp() + \
            forward_table() + nop_action()

    fwd_tbl = 'forward_table'

    action_name = 'mod_headers'
    program += benchmark_modify_header_overhead(action_name, nb_operations)

    table_name = 'test_tbl'
    match = 'udp.dstPort : exact;'
    actions = '\t\t_nop;\n\t\t{0};'.format(action_name)
    program += add_table(table_name, match, actions, 4)


    program += control(fwd_tbl, apply_table(table_name))

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands = add_default_rule(table_name, '_nop')
    # commands += add_rule(table_name, action_name, 319)
    commands += add_default_rule(table_name, action_name)
    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)
    get_set_field_pcap(out_dir, packet_size=128)
    generate_pisces_command(nb_operations, out_dir)

    return True
