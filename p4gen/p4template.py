from string import Template

def read_template(filename, binding={}):
    """
    This method and substitutes the variables in the template with the binding
    and returns the result of the substitution

    :param filename: The path to the template
    :type filename: string
    :param binding: the mapping of variables to their values
    :type binding: dictionary
    :returns:  str -- the code in plain text
    :raises: None

    """
    with open (filename, 'r') as code_template:
        src = Template(code_template.read())
    return src.substitute(binding)

def p4_define():
    """
    This method returns the constant definitions in P4

    :returns:  str -- the code in plain text
    :raises: None

    """
    p4_define = read_template('template/define.txt')
    return p4_define

def ethernet():
    """
    This method returns the Ethernet header definition and its parser

    :returns:  str -- the code in plain text
    :raises: None

    """
    ethernet_hdr = read_template('template/headers/ethernet.txt')
    parse_eth = read_template('template/parsers/parse_ethernet.txt')
    return (ethernet_hdr + parse_eth)

def ipv4():
    """
    This method returns the IPv4 header definition and its parser

    :returns:  str -- the code in plain text
    :raises: None

    """
    ipv4_hdr = read_template('template/headers/ipv4.txt')
    parse_ipv4 = read_template('template/parsers/parse_ipv4.txt')
    return (ipv4_hdr + parse_ipv4)

def tcp():
    """
    This method returns the TCP header definition and its parser

    :returns:  str -- the code in plain text
    :raises: None

    """
    tcp_hdr = read_template('template/headers/tcp.txt')
    parse_tcp = read_template('template/parsers/parse_tcp.txt')
    return (tcp_hdr + parse_tcp)

def udp(other_states=''):
    """
    This method returns the UDP header definition and its parser. It's possible
    to provide an option to a next state along the default ingress

    :param other_states: other options in 'return select' statement
    :type other_states: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    udp_hdr = read_template('template/headers/udp.txt')
    binding = {'other_states': other_states}
    parse_udp = read_template('template/parsers/parse_udp.txt', binding)
    return (udp_hdr + parse_udp)

def nop_action():
    """
    This method returns the _nop action definition

    :returns:  str -- the code in plain text
    :raises: None

    """
    return read_template('template/actions/nop.txt')

def forward_table():
    """
    This method returns the 'forwarding_table' definition

    :returns:  str -- the code in plain text
    :raises: None

    """
    d = { 'tbl_name': 'forward_table' }
    return read_template('template/tables/forward_table.txt', d)

def nop_table(tbl_name, tbl_size):
    """
    This method returns the table definition with only _nop action to benchmark
    the pipeline

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param tbl_size: the size of the table
    :type tbl_size: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'tbl_name': tbl_name, 'tbl_size': tbl_size}
    return read_template('template/tables/nop_table.txt', binding)

def new_table(tbl_name, matches='', actions='', tbl_size=1):
    """
    This method returns the table definition with generic match-actions

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param matches: the fields and matching method
    :type matches: str
    :param actions: the possible actions of the table
    :type actions: str
    :param tbl_size: the size of the table
    :type tbl_size: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {
        'tbl_name': tbl_name,
        'matches' : matches,
        'actions' : actions,
        'tbl_size': tbl_size}
    return read_template('template/tables/table.txt', binding)

def apply_table(tbl_name):
    """
    This method returns the apply statement used in the control flow

    :param tbl_name: the name of the table
    :type tbl_name: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    return read_template('template/controls/apply_table.txt', {'tbl_name': tbl_name})

def control(fwd_tbl, applies):
    """
    This method returns the apply statement and apply forward_table used in the control flow

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param applies: the apply statement for other table
    :type applies: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    d = { 'fwd_tbl' : fwd_tbl, 'applies': applies }
    return read_template('template/controls/ingress.txt', d)

def cli_commands(fwd_tbl, ):
    """
    This method returns the commands for installing rules of table

    :param fwd_tbl: the name of the forwarding table
    :type fwd_tbl: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    return read_template('template/commands/forward.txt', { 'fwd_tbl' : fwd_tbl})

def default_nop(tbl_name):
    """
    This method returns the command for installing the default action _nop for a table

    :param tbl_name: the name of the table
    :type tbl_name: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'tbl_name': tbl_name}
    return read_template('template/commands/default_nop.txt', binding)

def new_header(header_type_name, field_dec):
    """
    This method returns a header definition with its fields description

    :param header_type_name: the type name of the header
    :type header_type_name: str
    :param field_dec: the field description of the header
    :type field_dec: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'header_type_name': header_type_name, 'field_dec': field_dec}
    return read_template('template/headers/generic.txt', binding)

def new_metadata_instance(header_type_name, instance_name):
    """
    This method returns a code block that instantiates a metadata instance

    :param header_type_name: the type name of the header
    :type header_type_name: str
    :param instance_name: the identifier of the metadata
    :type instance_name: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'header_type_name': header_type_name, 'instance_name': instance_name}
    return read_template('template/headers/metadata.txt', binding)


def new_parser(header_type_name, header_name, parser_state_name, next_state):
    """
    This method returns a parser definition for a header

    :param header_type_name: the type name of the header
    :type header_type_name: str
    :param header_name: the name of a header instance
    :type header_name: str
    :param parser_state_name: the name of this parser
    :type parser_state_name: str
    :param next_state: the name of next parser
    :type next_state: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'header_type_name': header_type_name, 'header_name': header_name                      ,
             'parser_state_name': parser_state_name, 'next_state': next_state}
    return read_template('template/parsers/parse_generic.txt', binding)

def new_register(register_name, element_width, nb_element):
    """
    This method returns a register definition

    :param register_name: the name of the register
    :type register_name: str
    :param element_width: the size of an element in the register
    :type element_width: int
    :param nb_element: the number of elements in the register
    :type nb_element: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'register_name': register_name, 'element_width': element_width,
                 'nb_element': nb_element}
    return read_template('template/states/register.txt', binding)

def register_actions(read_set, write_set):
    """
    This method returns two action: read and write to a set of registers

    :param read_set: the action to read registers
    :type read_set: str
    :param write_set: the action to write to registers
    :type write_set: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'read_set' : read_set, 'write_set': write_set}
    return read_template('template/actions/register_actions.txt', binding)

def register_read(register, field, index):
    """
    This method returns a primitive action: read a register at a specific index

    :param register: the register name
    :type register: str
    :param field: the field to put the data to
    :type field: int
    :param index: the index on the register
    :type index: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'register' : register, 'field': field, 'index': index}
    return read_template('template/actions/read_action.txt', binding)

def register_write(register, field, index):
    """
    This method returns a primitive action: write a register at a specific index

    :param register: the register name
    :type register: str
    :param field: the field to get the data from
    :type field: int
    :param index: the index on the register
    :type index: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'register' : register, 'field': field, 'index': index}
    return read_template('template/actions/write_action.txt', binding)