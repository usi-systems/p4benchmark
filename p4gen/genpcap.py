from scapy.all import Packet, ShortField, XBitField
from scapy.all import Ether, IP, UDP, Padding
from scapy.all import wrpcap

def add_eth_ip_udp_headers(dport):
    eth = Ether(src='0C:C4:7A:A3:25:34', dst='0C:C4:7A:A3:25:35')
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

def vary_header_field(nb_fields):
    class P4Bench(Packet):
        name = "P4Bench Message"
        fields_desc =  []
        for i in range(nb_fields):
            fields_desc.append(ShortField('field_%d' % i , i))
    return P4Bench()

def add_padding(pkt, packet_size):
    pad_len = packet_size - len(pkt)
    if pad_len < 0:
        print "Packet size [%d] is greater than expected %d" % (len(pkt), packet_size)
    else:
        pad = Padding('\x00'*pad_len)
        pkt = pkt/pad
    return pkt

def get_parser_header_pcap(nb_fields, nb_headers, udp_dest_port, out_dir, packet_size=128):
    pkt = add_eth_ip_udp_headers(udp_dest_port)
    pkt /= add_layers(nb_fields, nb_headers)

    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)

def get_parser_field_pcap(nb_fields, udp_dest_port, out_dir, packet_size=128):
    pkt = add_eth_ip_udp_headers(udp_dest_port)
    pkt /= vary_header_field(nb_fields)

    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)

def get_read_state_pcap(udp_dest_port, out_dir, packet_size=128):

    class MemTest(Packet):
        name = "P4Bench Message for MemTest"
        fields_desc =  [
            XBitField("op", 0x1, 4),
            XBitField("index", 0x1, 12),
            XBitField("data", 0xf1f2f3f4, 32),
        ]

    pkt = add_eth_ip_udp_headers(udp_dest_port)
    pkt /= MemTest(op=2, index=0)

    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkts)

def get_write_state_pcap(udp_dest_port, out_dir, packet_size=128):

    class MemTest(Packet):
        name = "P4Bench Message for MemTest"
        fields_desc =  [
            XBitField("op", 0x1, 4),
            XBitField("index", 0x1, 12),
            XBitField("data", 0xf1f2f3f4, 32),
        ]

    pkt = add_eth_ip_udp_headers(udp_dest_port)

    pkt /= MemTest(op=1, index=0, data=0)

    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)

def get_pipeline_pcap(out_dir, packet_size=128):
    pkt = add_eth_ip_udp_headers(15432)
    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)


def get_packetmod_pcap(nb_headers, nb_fields, mod_type, out_dir, packet_size=128):
    pkt = Packet()
    if mod_type == 'add':
        pkt = add_eth_ip_udp_headers(15432)
    elif mod_type == 'rm':
        pkt = add_eth_ip_udp_headers(0x9091)
        pkt /= add_layers(nb_fields, nb_headers)
        pkt = add_padding(pkt, packet_size)
    elif mod_type == 'mod':
        pkt = add_eth_ip_udp_headers(0x9091)
        pkt /= add_layers(nb_fields, nb_headers)
        pkt = add_padding(pkt, packet_size)

    wrpcap('%s/test.pcap' % out_dir, pkt)
