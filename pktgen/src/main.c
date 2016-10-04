#include <getopt.h>
#include <string.h>
#include <pthread.h>
#include <time.h>

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
print_app_usage(const char *app_name)
{

    printf("Usage: %s   [-i interface] [-p pcap_file] [-f filter_exp]\n", app_name);
    printf("\n");
    printf("Requires:\n");
    printf("-i    interface    Listen on <interface> for packets.\n");
    printf("-p    pcap_file    The pcap file for benchmarking the P4 program.\n");
    printf("Options:\n");
    printf("-f    filter_exp   Capture packets that match filter expression.\n");
    printf("\n");

    return;
}

static struct {
    int   count;
    int   interval;
    char* pcap_file;
    char* interface;
    char* filter_exp;
} config;

static void free_config() {
    free(config.pcap_file);
    free(config.interface);
    free(config.filter_exp);
}

/* Parse the arguments given in the command line of the application */
void parse_args(int argc, char **argv)
{
    int opt;
    const char *app_name = argv[0];
    config.count = 1;
    config.interval = 1000000; /* 1 ms */
    /* Parse command line */
    while ((opt = getopt(argc, argv, "c:i:p:f:t:")) != EOF) {
        switch (opt) {
        case 'c':
            config.count = atoi(optarg);
            break;
        case 't':
            config.interval = atoi(optarg);
            break;
        case 'i':
            config.interface = strdup(optarg);
            break;
        case 'p':
            config.pcap_file = strdup(optarg);
            break;
        case 'f':
            config.filter_exp = strdup(optarg);
            break;
        default:
            print_app_usage(app_name);
            exit(EXIT_FAILURE);
        }
    }
    if (config.interface == NULL || config.pcap_file == NULL) {
        print_app_usage(app_name);
        exit(EXIT_FAILURE);
    }
}

void *sniff(void *arg)
{
    pcap_t *handle = (pcap_t*) arg;
    /* now we can set our callback function */
    pcap_loop(handle, config.count, got_packet, NULL);

    return NULL;
}

int main(int argc, char* argv[])
{
    print_app_banner(argv[0]);
    parse_args(argc, argv);
    pthread_t sniff_thread;

    pcap_t *input_packets = read_pcap(config.pcap_file);

    struct bpf_program fp;    
    pcap_t *handle = init_dev(&fp, config.interface, config.filter_exp);

    if (pthread_create(&sniff_thread, NULL, sniff, handle) < 0) {
        fprintf(stderr, "Error creating thread\n");
        exit(EXIT_FAILURE);
    }

    const unsigned char *packet;
    struct pcap_pkthdr header;
    /* Now just loop through extracting packets as long as we have
     * some to read.
     */
     struct timespec interval = {0, config.interval}, remaining;

    int i;
    while ((packet = pcap_next(input_packets, &header)) != NULL)
        for (i = 0 ; i < config.count; i++) {
            pcap_inject(handle, packet, header.caplen);
            printf("Sent packet %.6d\n", i);
            nanosleep(&interval, &remaining);
        }


    if (pthread_join(sniff_thread, NULL)) {
        fprintf(stderr, "Error joining thread\n");
        exit(EXIT_FAILURE);
    }

    /* cleanup */
    pcap_freecode(&fp);
    pcap_close(handle);
    pcap_close(input_packets);
    free_config();

    return 0;
}