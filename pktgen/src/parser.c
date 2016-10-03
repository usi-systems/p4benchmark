/* Demonstration program of reading packet trace files recorded by pcap
 * (used by tshark and tcpdump) and dumping out some corresponding information
 * in a human-readable form.
 *
 * Note, this program is limited to processing trace files that contains
 * UDP packets.  It prints the timestamp, source port, destination port,
 * and length of each such packet.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <netinet/in.h>
#include <netinet/ip.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <netinet/udp.h>

#include <pcap.h>

#include "parser.h"

void dump_udp_packet(const unsigned char *packet, struct timeval ts,
			unsigned int capture_len)
{
	struct ip *ip;
	struct udphdr *udp;
	unsigned int IP_header_length;

	/* For simplicity, we assume Ethernet encapsulation. */

	if (capture_len < sizeof(struct ether_header))
	{
		/* We didn't even capture a full Ethernet header, so we
		 * can't analyze this any further.
		 */
		too_short(ts, "Ethernet header");
		return;
	}

	/* Skip over the Ethernet header. */
	packet += sizeof(struct ether_header);
	capture_len -= sizeof(struct ether_header);

	if (capture_len < sizeof(struct ip))
	{ /* Didn't capture a full IP header */
		too_short(ts, "IP header");
		return;
	}

	ip = (struct ip*) packet;
	IP_header_length = ip->ip_hl * 4;	/* ip_hl is in 4-byte words */

	if (capture_len < IP_header_length)
	{ /* didn't capture the full IP header including options */
		too_short(ts, "IP header with options");
		return;
	}

	if (ip->ip_p != IPPROTO_UDP)
	{
		problem_pkt(ts, "non-UDP packet");
		return;
	}

	/* Skip over the IP header to get to the UDP header. */
	packet += IP_header_length;
	capture_len -= IP_header_length;

	if (capture_len < sizeof(struct udphdr))
	{
		too_short(ts, "UDP header");
		return;
	}

	udp = (struct udphdr*) packet;

	printf("%s UDP src_port=%d dst_port=%d length=%d\n",
		timestamp_string(ts),
		ntohs(udp->uh_sport),
		ntohs(udp->uh_dport),
		ntohs(udp->uh_ulen));
}


int read_pcap(char* pcap_path)
{
	pcap_t *pcap;
	const unsigned char *packet;
	char errbuf[PCAP_ERRBUF_SIZE];
	struct pcap_pkthdr header;


	pcap = pcap_open_offline(pcap_path, errbuf);
	if (pcap == NULL)
	{
		fprintf(stderr, "error reading pcap file: %s\n", errbuf);
		exit(1);
	}

	/* Now just loop through extracting packets as long as we have
	 * some to read.
	 */
	while ((packet = pcap_next(pcap, &header)) != NULL)
		dump_udp_packet(packet, header.ts, header.caplen);

	return 0;
}


/* Note, this routine returns a pointer into a static buffer, and
 * so each call overwrites the value returned by the previous call.
 */
const char *timestamp_string(struct timeval ts)
{
	static char timestamp_string_buf[256];

	sprintf(timestamp_string_buf, "%d.%06d",
		(int) ts.tv_sec, (int) ts.tv_usec);

	return timestamp_string_buf;
}

void problem_pkt(struct timeval ts, const char *reason)
{
	fprintf(stderr, "%s: %s\n", timestamp_string(ts), reason);
}

void too_short(struct timeval ts, const char *truncated_hdr)
{
	fprintf(stderr, "packet with timestamp %s is truncated and lacks a full %s\n",
		timestamp_string(ts), truncated_hdr);
}
