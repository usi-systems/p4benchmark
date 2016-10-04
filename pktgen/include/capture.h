#ifndef _CAPTURE_H_
#define _CAPTURE_H_

#include <stdlib.h>
#include <pcap.h>

/* default snap length (maximum bytes per packet to capture) */
#define SNAP_LEN 1518

/* ethernet headers are always exactly 14 bytes [1] */
#define SIZE_ETHERNET 14

void
print_timeval(char* msg, struct timeval *tv);

void
got_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet);

void
print_payload(const u_char *payload, int len);

void
print_hex_ascii_line(const u_char *payload, int len, int offset);

int
capture(char *dev, char* filter_exp);

pcap_t*
init_dev(struct bpf_program *fp, char *dev, char* filter_exp);

#endif