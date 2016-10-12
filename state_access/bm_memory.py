import os
from subprocess import call
from pkg_resources import resource_filename

from p4gen.genpcap import get_write_state_pcap, get_read_state_pcap
from p4gen.p4template import *
from p4gen import copy_scripts

def add_registers(nb_registers, element_width, nb_elements, nb_operations,
        field, index):
    """
    This method generate the P4 code of register declaration and register actions

    :param nb_registers: the number of registers included in the program
    :type nb_registers: int
    :param element_width: the size of each register element
    :type element_width: int
    :param nb_elements: the number of elements in each register
    :type nb_elements: int
    :param nb_operations: the number of operations to the registers
    :type nb_operations: int
    :param field: the reference field for register read or write
    :type field: str
    :param index: the index of register element involving in the operation
    :type index: int
    :returns: bool -- True if there is no error

    """
    code_block = ''
    read_set = ''
    write_set = ''
    for i in range(nb_registers):
        register_name = 'register_%d' % i
        code_block += add_register(register_name, element_width, nb_elements)
        for j in range(nb_operations):
            read_set  += register_read(register_name, field, index)
            write_set += register_write(register_name, field, index)

    code_block += register_actions(read_set, write_set)
    return code_block


def benchmark_memory(nb_registers, element_width, nb_elements, nb_operations, write_op=False):
    """
    This method generate the P4 program to benchmark memory consumption

    :param nb_registers: the number of registers included in the program
    :type nb_registers: int
    :param element_width: the size of each register element
    :type element_width: int
    :param nb_elements: the number of elements in each register
    :type nb_elements: int
    :param nb_elements: the number of operations to the registers
    :type nb_elements: int
    :returns: bool -- True if there is no error

    """
    udp_dport = 0x9091
    out_dir = 'output'
    if not os.path.exists(out_dir):
       os.makedirs(out_dir)

    fwd_tbl = 'forward_table'

    program = p4_define() + ethernet() + ipv4() + tcp()
    header_type_name = 'memtest_t'
    header_name = 'memtest'
    parser_state_name = 'parse_memtest'
    field_dec  = add_header_field('register_op', 4)
    field_dec += add_header_field('index', 12)
    field_dec += add_header_field('data', element_width)

    program += udp(select_case(udp_dport, parser_state_name))
    program += add_header(header_type_name, field_dec)
    program += add_parser_without_select(header_type_name, header_name,
                    parser_state_name, 'ingress')

    # metadata = 'mem_metadata'
    # program += add_metadata_instance(header_type_name, metadata)
    field = '%s.data' % header_name
    index = '%s.index' % header_name

    program += nop_action()

    program += add_registers(nb_registers, element_width, nb_elements, nb_operations,
                    field, index)

    match_field = '%s.register_op' % header_name
    matches = '%s : exact;' % match_field
    actions = 'get_value; put_value; _nop;'
    table_name = 'register_table'
    program += add_table(table_name, matches, actions, 3)
    applies = apply_table(table_name)

    program += forward_table()
    program += control(fwd_tbl, applies)

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands = ''
    commands += cli_commands(fwd_tbl)
    commands += add_rule(table_name, '_nop', 0)
    commands += add_rule(table_name, 'get_value', 1)
    commands += add_rule(table_name, 'put_value', 2)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)
    if write_op:
        get_write_state_pcap(udp_dport, out_dir)
    else:
        get_read_state_pcap(udp_dport, out_dir)

    return True
