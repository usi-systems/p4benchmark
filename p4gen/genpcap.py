from scapy.all import Packet, ShortField, XBitField
from scapy.all import Ether, IP, UDP
from scapy.all import wrpcap

def add_eth_ip_udp_headers(dport):
    eth = Ether(dst='00:00:00:00:00:02')
    ip  = IP(dst='10.0.0.2', ttl=64)
    udp = UDP(sport=65231, dport=dport)
    pkt = eth / ip / udp
    return pkt

def add_layers(nb_fields, nb_headers):
    class P4Bench(Packet):
        name = "P4Bench Message"
        fields_desc =  []
        for i in range(nb_fields):
            fields_desc.append(ShortField('field_%d' %i , 0))
    layers = ''
    for i in range(nb_headers):
        if i < (nb_headers - 1):
            layers = layers / P4Bench(field_0=1)
        else:
            layers = layers / P4Bench(field_0=0)
    return layers

def get_parser_pcap(nb_fields, nb_headers, udp_dest_port, out_dir):
    pkt = add_eth_ip_udp_headers(udp_dest_port)
    pkt /= add_layers(nb_fields, nb_headers)
    wrpcap('%s/parser.pcap' % out_dir, pkt)

def get_state_pcap(udp_dest_port, out_dir):

    class MemTest(Packet):
        name = "P4Bench Message for MemTest"
        fields_desc =  [
            XBitField("op", 0x1, 4),
            XBitField("index", 0x1, 12),
            XBitField("data", 0xf1f2f3f4, 32),
        ]

    pkt = add_eth_ip_udp_headers(udp_dest_port)

    no_op = pkt / MemTest(op=0)
    set_data = pkt / MemTest(op=2, index=0)
    get_data = pkt / MemTest(op=1, index=0, data=0)

    pkts = [ no_op, set_data, get_data ]
    wrpcap('%s/state.pcap' % out_dir, pkts)

def get_pipeline_pcap(out_dir):
    pkt = add_eth_ip_udp_headers(15432) / "PIPELINE"
    wrpcap('%s/pipeline.pcap' % out_dir, pkt)

def get_packetmod_pcap(nb_headers, nb_fields, mod_type, out_dir):
    pkt = Packet()
    if mod_type == 'add':
        pkt = add_eth_ip_udp_headers(15432)
    elif mod_type == 'rm':
        pkt = add_eth_ip_udp_headers(0x9091)
        pkt /= add_layers(nb_fields, nb_headers)
    elif mod_type == 'mod':
        pkt = add_eth_ip_udp_headers(0x9091)
        pkt /= add_layers(nb_fields, nb_headers)

    wrpcap('%s/pktmod.pcap' % out_dir, pkt)

