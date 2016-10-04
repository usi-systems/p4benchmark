#include <pcap.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>

#include <sys/time.h>
#include "capture.h"


/*
 * print data in rows of 16 bytes: offset   hex   ascii
 *
 * 00000   47 45 54 20 2f 20 48 54  54 50 2f 31 2e 31 0d 0a   GET / HTTP/1.1..
 */
void
print_hex_ascii_line(const u_char *payload, int len, int offset)
{

    int i;
    int gap;
    const u_char *ch;

    /* offset */
    printf("%05d   ", offset);
    
    /* hex */
    ch = payload;
    for(i = 0; i < len; i++) {
        printf("%02x ", *ch);
        ch++;
        /* print extra space after 8th byte for visual aid */
        if (i == 7)
            printf(" ");
    }
    /* print space to handle line less than 8 bytes */
    if (len < 8)
        printf(" ");
    
    /* fill hex gap with spaces if not full line */
    if (len < 16) {
        gap = 16 - len;
        for (i = 0; i < gap; i++) {
            printf("   ");
        }
    }
    printf("   ");
    
    /* ascii (if printable) */
    ch = payload;
    for(i = 0; i < len; i++) {
        if (isprint(*ch))
            printf("%c", *ch);
        else
            printf(".");
        ch++;
    }

    printf("\n");

return;
}

/*
 * print packet payload data (avoid printing binary data)
 */
void
print_payload(const u_char *payload, int len)
{

    int len_rem = len;
    int line_width = 16;            /* number of bytes per line */
    int line_len;
    int offset = 0;                 /* zero-based offset counter */
    const u_char *ch = payload;

    if (len <= 0)
        return;

    /* data fits on one line */
    if (len <= line_width) {
        print_hex_ascii_line(ch, len, offset);
        return;
    }

    /* data spans multiple lines */
    for ( ;; ) {
        /* compute current line length */
        line_len = line_width % len_rem;
        /* print line */
        print_hex_ascii_line(ch, line_len, offset);
        /* compute total remaining */
        len_rem = len_rem - line_len;
        /* shift pointer to remaining bytes to print */
        ch = ch + line_len;
        /* add offset */
        offset = offset + line_width;
        /* check if we have line width chars or less */
        if (len_rem <= line_width) {
            /* print last line and get out */
            print_hex_ascii_line(ch, len_rem, offset);
            break;
        }
    }

return;
}

void print_timeval(char* msg, struct timeval *tv) {
    printf("%s<%ld.%06ld>\n", msg, (long int)(tv->tv_sec), (long int)(tv->tv_usec));
}

void
print_ip_info(struct ip *ip)
{
    /* print source and destination IP addresses */
    printf("       From: %s\n", inet_ntoa(ip->ip_src));
    printf("         To: %s\n", inet_ntoa(ip->ip_dst));
}

void
handle_udp_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet)
{
    int tv_offset = header->caplen - sizeof(struct timeval);
    struct timeval* tv = (struct timeval*)(packet + tv_offset);
    static struct timeval res;
    timersub(&header->ts, tv, &res);

    print_timeval("Latency", &res);
}

void
handle_tcp_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet,
        const struct ip *ip, int size_ip)
{
    const struct tcphdr *tcp;             /* The TCP header */
    const u_char *payload;                /* Packet payload */
    int size_tcp;
    int size_payload;
    /* define/compute tcp header offset */
    tcp = (struct tcphdr*)(packet + SIZE_ETHERNET + size_ip);
    size_tcp = (tcp->th_off)*4;
    if (size_tcp < 20) {
        printf("   * Invalid TCP header length: %u bytes\n", size_tcp);
        return;
    }

    printf("   Src port: %d\n", ntohs(tcp->th_sport));
    printf("   Dst port: %d\n", ntohs(tcp->th_dport));

    /* define/compute tcp payload (segment) offset */
    payload = (u_char *)(packet + SIZE_ETHERNET + size_ip + size_tcp);

    /* compute tcp payload (segment) size */
    size_payload = ntohs(ip->ip_len) - (size_ip + size_tcp);

    /*
     * Print payload data; it might be binary, so don't just
     * treat it as a string.
     */
    if (size_payload > 0) {
        printf("   Payload (%d bytes):\n", size_payload);
        print_payload(payload, size_payload);
    }
}

/*
 * dissect/print packet
 */
void
got_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet)
{

    static int count = 1;                   /* packet counter */
    
    /* declare pointers to packet headers */
    const struct ether_header *ethernet;  /* The ethernet header [1] */
    const struct ip *ip;                  /* The IP header */

    int size_ip;
    
    printf("\nPacket number %d:\n", count);
    count++;
    
    /* define ethernet header */
    ethernet = (struct ether_header*)(packet);

    u_short ether_type = ntohs(ethernet->ether_type);

    if (ether_type != ETHERTYPE_IP)
        return;
    /* define/compute ip header offset */
    ip = (struct ip*)(packet + SIZE_ETHERNET);
    size_ip = (ip->ip_hl)*4;
    if (size_ip < 20) {
        printf("   * Invalid IP header length: %u bytes\n", size_ip);
        return;
    }
    
    /* determine protocol */    
    switch(ip->ip_p) {
        case IPPROTO_TCP:
            printf("   Protocol: TCP\n");
            handle_tcp_packet(args, header, packet, ip, size_ip);
            break;
        case IPPROTO_UDP:
            handle_udp_packet(args, header, packet);
            break;
        case IPPROTO_ICMP:
            printf("   Protocol: ICMP\n");
            return;
        case IPPROTO_IP:
            printf("   Protocol: IP\n");
            return;
        default:
            printf("   Protocol: unknown\n");
            return;
    }

    return;
}

/*
 * Initialize a device and return a pcap handler
 */
pcap_t*
init_dev(struct bpf_program *fp, char *dev, char* filter_exp)
{
    pcap_t *handle;
    char errbuf[PCAP_ERRBUF_SIZE];  /* error buffer */
    bpf_u_int32 mask;               /* subnet mask */
    bpf_u_int32 net;                /* ip */

    /* get network number and mask associated with capture device */
    if (pcap_lookupnet(dev, &net, &mask, errbuf) == -1) {
        fprintf(stderr, "Couldn't get netmask for device %s: %s\n",
            dev, errbuf);
        net = 0;
        mask = 0;
    }

    /* open capture device */
    handle = pcap_open_live(dev, SNAP_LEN, 1, 1000, errbuf);
    if (handle == NULL) {
        fprintf(stderr, "Couldn't open device %s: %s\n", dev, errbuf);
        exit(EXIT_FAILURE);
    }

    /* make sure we're capturing on an Ethernet device [2] */
    if (pcap_datalink(handle) != DLT_EN10MB) {
        fprintf(stderr, "%s is not an Ethernet\n", dev);
        exit(EXIT_FAILURE);
    }

    /* compile the filter expression */
    if (pcap_compile(handle, fp, filter_exp, 0, net) == -1) {
        fprintf(stderr, "Couldn't parse filter %s: %s\n",
            filter_exp, pcap_geterr(handle));
        exit(EXIT_FAILURE);
    }

    /* apply the compiled filter */
    if (pcap_setfilter(handle, fp) == -1) {
        fprintf(stderr, "Couldn't install filter %s: %s\n",
            filter_exp, pcap_geterr(handle));
        exit(EXIT_FAILURE);
    }

    return handle;
}

/*
 * Start capture on dev
 */
int capture(char *dev, char* filter_exp)
{
    pcap_t *handle;
    struct bpf_program fp;          /* compiled filter program (expression) */
    handle = init_dev(&fp, dev, filter_exp); /* initialize the device for capturing */

    int num_packets = 10;           /* number of packets to capture */
    /* now we can set our callback function */
    pcap_loop(handle, num_packets, got_packet, NULL);
    /* cleanup */
    pcap_freecode(&fp);
    pcap_close(handle);

    printf("\nCapture complete.\n");

return 0;
}
