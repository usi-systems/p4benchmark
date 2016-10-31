#include <getopt.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>
#include "capture.h"
#include "parser.h"

#define APP_DESC        "Benchmarking P4 programs"
#define APP_COPYRIGHT   "Copyright (c) 2016 Universit{a} della Svizzera italiana"
#define APP_DISCLAIMER  "THERE IS ABSOLUTELY NO WARRANTY FOR THIS PROGRAM."

#define APP_INFO    1
#define APP_DEBUG   2

static int force_quit = 0;
static int idle_timeout = 3;
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
    printf("-o    output_fn    The output file name (stat).\n");
    printf("Options:\n");
    printf("-c    count        Send \'count\' number of packets .\n");
    printf("-f    filter_exp   Capture packets that match filter expression.\n");
    printf("-l    log_level    Set log level { 1: INFO, 2: DEBUG }\n");
    printf("-s    interface    Send packets out of <interface>.\n");
    printf("-t    throughput   Limit the sending rate.\n");
    printf("\n");

    return;
}

static struct {
    int   count;
    int   bps;
    int   log_level;
    int   outstanding;
    char* pcap_file;
    char* interface;
    char* send_interface;
    char* filter_exp;
    char* output_fn;
} config;

struct app {
    int count;
    // pthread_mutex_t mutex_stat;
    struct pcap_pkthdr header;
    pcap_t* sniff;
    pcap_t* out;
    FILE *fp;
    const unsigned char* packet;
};

static void free_config() {
    free(config.pcap_file);
    free(config.interface);
    free(config.send_interface);
    free(config.filter_exp);
    free(config.output_fn);
}

#define US_PER_S 1000000
static struct {
    unsigned long nb_packets;
    unsigned long latency;
    unsigned long total_packets;
    float duration;
} stat;

/* Parse the arguments given in the command line of the application */
void parse_args(int argc, char **argv)
{
    int opt;
    const char *app_name = argv[0];
    config.count = 1;
    config.bps = 1;
    config.outstanding = 1;
    config.log_level = APP_INFO;
    /* Parse command line */
    while ((opt = getopt(argc, argv, "c:t:l:i:s:p:f:o:n:")) != EOF) {
        switch (opt) {
        case 'c':
            config.count = atoi(optarg);
            break;
        case 't':
            config.bps = atoi(optarg);
            break;
        case 'l':
            config.log_level = atoi(optarg);
            break;
        case 'i':
            config.interface = strdup(optarg);
            break;
        case 'n':
            config.outstanding = atoi(optarg);
            break;
        case 's':
            config.send_interface = strdup(optarg);
            break;
        case 'p':
            config.pcap_file = strdup(optarg);
            break;
        case 'f':
            config.filter_exp = strdup(optarg);
            break;
        case 'o':
            config.output_fn = strdup(optarg);
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
    if (config.output_fn == NULL)
        config.output_fn = strdup("stat.csv");
}

void average_latency(struct app* ctx)
{

    if (stat.nb_packets <= 0) {
        if (idle_timeout-- > 0)
            return;
        /* quite after three attempts */
        force_quit = 1;
        return;
    }
    // pthread_mutex_lock(&ctx->mutex_stat);
    float avg_us = (float) stat.latency / stat.nb_packets;
    fprintf(ctx->fp, "%lu,%f\n", stat.nb_packets, avg_us);
    stat.total_packets += stat.nb_packets;
    /* reset counter */
    stat.nb_packets = 0;
    stat.latency = 0;
    // pthread_mutex_unlock(&ctx->mutex_stat);
}

void
send_packet(struct app* app_ctx) {
    struct timeval tv;
    size_t buflen = app_ctx->header.caplen + sizeof(struct timeval);
    unsigned char buf[buflen];
    memcpy(buf, app_ctx->packet, app_ctx->header.caplen);
    gettimeofday(&tv, NULL);
    memcpy(buf + app_ctx->header.caplen, &tv, sizeof(struct timeval));
    pcap_inject(app_ctx->out, buf, buflen);
}

void
process_pkt(u_char *arg, const struct pcap_pkthdr *header, const u_char *packet)
{
    struct app* app_ctx = (struct app*) arg;

    if (force_quit) {
        pcap_breakloop(app_ctx->sniff);
        if (app_ctx->out)
            pcap_breakloop(app_ctx->out);
    }

    int tv_offset = header->caplen - sizeof(struct timeval);
    struct timeval* tv = (struct timeval*)(packet + tv_offset);
    static struct timeval res;
    timersub(&header->ts, tv, &res);
    fprintf(stdout, "%d.%06d\n", (int) res.tv_sec, (int) res.tv_usec);

    // pthread_mutex_lock(&app_ctx->mutex_stat);
    stat.latency += US_PER_S * res.tv_sec + res.tv_usec;
    stat.total_packets++;
    // pthread_mutex_unlock(&app_ctx->mutex_stat);
    send_packet(app_ctx);
}

void final_report(int total_sent)
{
    float lost = (total_sent - stat.total_packets) / (float)total_sent;
    float throughput = stat.total_packets / stat.duration;
    fprintf(stderr, "%-10d %-10lu %-10.3f %f\n",
        total_sent, stat.total_packets, lost, throughput);
}

void* sniff(void *arg)
{
    struct app* app_ctx = (struct app*) arg;
    int ret;
    /* now we can set our callback function */
    struct timeval start_tv, end_tv, res;
    gettimeofday(&start_tv, NULL);
    ret = pcap_loop(app_ctx->sniff, app_ctx->count, process_pkt,
        (u_char*)app_ctx);
    if (ret == -1)
        fprintf(stderr, "Error pcap_loop\n");
    gettimeofday(&end_tv, NULL);
    timersub(&end_tv, &start_tv, &res);
    stat.duration = res.tv_sec + (float)res.tv_usec / US_PER_S;

    force_quit = 1;
    return NULL;
}

void signal_handler(int signum)
{
    if (signum == SIGINT) {
        printf("\n\nSignal %d received, preparing to exit...\n", signum);
        force_quit = 1;
    }
}

void* report_stat(void *arg)
{
    struct app* ctx = (struct app *)arg;
    while(!force_quit) {
        average_latency(ctx);
        sleep(1);
    }

    return NULL;
}

int count_packets(char *path_to_trace)
{
    int counter = 0;
    struct pcap_pkthdr header;
    const unsigned char *packet;
    pcap_t *trace = read_pcap(path_to_trace);
    while ((packet = pcap_next(trace, &header)) != NULL) {
        counter++;
    }
    return counter;
}

int main(int argc, char* argv[])
{
    parse_args(argc, argv);

    if (config.log_level == APP_DEBUG)
        print_app_banner(argv[0]);

    // pthread_t sniff_thread, stat_thread;

    signal(SIGTERM, signal_handler);
    signal(SIGINT, signal_handler);

    struct app app_ctx;
    app_ctx.count = config.count * count_packets(config.pcap_file);

    pcap_t *input_packets = read_pcap(config.pcap_file);
    /* Now just loop through extracting packets as long as we have
     * some to read.
     */
    app_ctx.packet = pcap_next(input_packets, &app_ctx.header);
    fprintf(stderr, "packet-size %d\n", app_ctx.header.caplen);

    int bufsize = app_ctx.header.caplen + sizeof(struct timeval);

    struct bpf_program fp;
    app_ctx.sniff = init_dev_bufsize(&fp, config.interface, config.filter_exp, bufsize, 0.001);


    #ifdef WRITE_TO_FILE
        app_ctx.fp = fopen(config.output_fn, "w");
    #else
        app_ctx.fp = stdout;
    #endif

    if (app_ctx.fp == NULL) {
        fprintf(stderr, "Error Opening file to write\n");
        exit(EXIT_FAILURE);
    }

    if (config.send_interface != NULL) {
        struct bpf_program send_fp;
        app_ctx.out = init_dev_bufsize(&send_fp, config.send_interface, NULL, bufsize, 0.001);
    } else {
        app_ctx.out = app_ctx.sniff;
    }

    int i;
    for (i = 0; i < config.outstanding; i++)
        send_packet(&app_ctx);

    // pthread_mutex_init(&app_ctx.mutex_stat, NULL);

    // if (pthread_create(&sniff_thread, NULL, sniff, &app_ctx) < 0) {
    //     fprintf(stderr, "Error creating sniff thread\n");
    //     exit(EXIT_FAILURE);
    // }

    // if (pthread_create(&stat_thread, NULL, report_stat, &app_ctx) < 0) {
    //     fprintf(stderr, "Error creating report thread\n");
    //     exit(EXIT_FAILURE);
    // }
    sniff(&app_ctx);

    while(!force_quit) {
        /* wait for SIGTERM or SIGINT */
        sleep(1);
    }


    // if (pthread_join(sniff_thread, NULL)) {
    //     fprintf(stderr, "Error joining thread\n");
    //     exit(EXIT_FAILURE);
    // }
    // if (pthread_join(stat_thread, NULL)) {
    //     fprintf(stderr, "Error joining thread\n");
    //     exit(EXIT_FAILURE);
    // }

    final_report(app_ctx.count);

    if (config.log_level == APP_DEBUG)
        printf("Cleanup\n");
    /* cleanup */
    pcap_freecode(&fp);
    pcap_close(app_ctx.sniff);
    if (config.send_interface != NULL)
        pcap_close(app_ctx.out);
    pcap_close(input_packets);
    free_config();

    #ifdef WRITE_TO_FILE
        fclose(app_ctx.fp);
    #endif
    // pthread_mutex_destroy(&app_ctx.mutex_stat);
    // pthread_exit(NULL);

    return 0;
}