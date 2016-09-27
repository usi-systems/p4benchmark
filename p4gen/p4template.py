from string import Template

def read_template(filename, binding={}):
    with open (filename, 'r') as code_template:
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

def udp(other_states=''):
    udp_hdr = read_template('template/headers/udp.txt')
    binding = {'other_states': other_states}
    parse_udp = read_template('template/parsers/parse_udp.txt', binding)
    return (udp_hdr + parse_udp)

def nop_action():
    return read_template('template/actions/nop.txt')

def forward_table():
    d = { 'tbl_name': 'forward_table' }
    return read_template('template/tables/forward_table.txt', d)

def nop_table(tbl_name, tbl_size):
    binding = {'tbl_name': tbl_name, 'tbl_size': tbl_size}
    return read_template('template/tables/nop_table.txt', binding)

def new_table(tbl_name, matches='', actions='', tbl_size=1):
    binding = {
        'tbl_name': tbl_name,
        'matches' : matches,
        'actions' : actions,
        'tbl_size': tbl_size}
    return read_template('template/tables/table.txt', binding)

def apply_table(tbl_name):
    return read_template('template/controls/apply_table.txt', {'tbl_name': tbl_name})

def control(fwd_tbl, applies):
    d = { 'fwd_tbl' : fwd_tbl, 'applies': applies }
    return read_template('template/controls/ingress.txt', d)

def cli_commands(fwd_tbl, ):
    return read_template('template/commands/forward.txt', { 'fwd_tbl' : fwd_tbl})

def default_nop(tbl_name):
    binding = {'tbl_name': tbl_name}
    return read_template('template/commands/default_nop.txt', binding)

def new_header(header_type_name, field_dec):
    binding = {'header_type_name': header_type_name, 'field_dec': field_dec}
    return read_template('template/headers/generic.txt', binding)

def new_parser(header_type_name, header_name, parser_state_name, next_state):
    binding = {'header_type_name': header_type_name, 'header_name': header_name                      ,
             'parser_state_name': parser_state_name, 'next_state': next_state}
    return read_template('template/parsers/parse_generic.txt', binding)

def new_register(register_name, element_width, nb_element):
    binding = {'register_name': register_name, 'element_width': element_width,
                 'nb_element': nb_element}
    return read_template('template/states/register.txt', binding)

def register_actions(read_set, write_set):
    binding = {'read_set' : read_set, 'write_set': write_set}
    return read_template('template/actions/register_actions.txt', binding)

def register_read(register, field, index):
    binding = {'register' : register, 'field': field, 'index': index}
    return read_template('template/actions/read_action.txt', binding)

def register_write(register, field, index):
    binding = {'register' : register, 'field': field, 'index': index}
    return read_template('template/actions/write_action.txt', binding)