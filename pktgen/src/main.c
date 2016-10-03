#include "capture.h"
#include "parser.h"

#define APP_DESC        "Benchmarking P4 programs"
#define APP_COPYRIGHT   "Copyright (c) 2016 Universit{a} della Svizzera italiana"
#define APP_DISCLAIMER  "THERE IS ABSOLUTELY NO WARRANTY FOR THIS PROGRAM."

/*
 * app name/banner
 */
void
print_app_banner(char *app_name)
{

    printf("%s - %s\n", app_name, APP_DESC);
    printf("%s\n", APP_COPYRIGHT);
    printf("%s\n", APP_DISCLAIMER);
    printf("\n");

    return;
}

/*
 * print help text
 */
void
print_app_usage(char *app_name)
{

    printf("Usage: %s  pcap-file interface filter-exp\n", app_name);
    printf("\n");
    printf("Parameters:\n");
    printf("    pcap-file    The pcap file for benchmarking the P4 program.\n");
    printf("    interface    Listen on <interface> for packets.\n");
    printf("    filter-exp   Capture packets that match filter expression.\n");
    printf("\n");

    return;
}

int main(int argc, char* argv[])
{
    print_app_banner(argv[0]);

    if (argc < 4) {
        print_app_usage(argv[0]);
        exit(EXIT_SUCCESS);
    }

    pcap_t *input_packets = read_pcap(argv[1]);


    struct bpf_program fp;    
    pcap_t *handle = init_dev(&fp, argv[2], argv[3]);


    const unsigned char *packet;
    struct pcap_pkthdr header;
    /* Now just loop through extracting packets as long as we have
     * some to read.
     */
    while ((packet = pcap_next(input_packets, &header)) != NULL)
        pcap_inject(handle, packet, header.caplen);
        // dump_udp_packet(packet, header.ts, header.caplen);

    // capture(argv[2], argv[3]);

    /* cleanup */
    pcap_freecode(&fp);
    pcap_close(handle);
    pcap_close(input_packets);

    return 0;
}