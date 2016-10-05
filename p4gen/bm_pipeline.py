import os
from subprocess import call
from pkg_resources import resource_filename

from p4template import *
import genpcap

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

    call(['cp', resource_filename(__name__, 'template/run_switch.sh'), out_dir])
    call(['cp', resource_filename(__name__, 'template/run_test.py'), out_dir])
    genpcap.get_pipeline_pcap(out_dir)

    return True