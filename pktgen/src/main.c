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
    printf("-f    filter_exp   Capture packets that match filter expression.\n");
    printf("\n");

    return;
}

static struct {
    int   count;
    int   bps;
    int   log_level;
    char* pcap_file;
    char* interface;
    char* filter_exp;
    char* output_fn;
} config;

struct app {
    int count;
    pthread_mutex_t mutex_stat;
    pcap_t* sniff;
    FILE *fp;
};

static void free_config() {
    free(config.pcap_file);
    free(config.interface);
    free(config.filter_exp);
    free(config.output_fn);
}

#define US_PER_S 1000000
static struct {
    unsigned long nb_packets;
    unsigned long latency;
    unsigned long total_packets;
} stat;

/* Parse the arguments given in the command line of the application */
void parse_args(int argc, char **argv)
{
    int opt;
    const char *app_name = argv[0];
    config.count = 1;
    config.bps = 1;
    config.log_level = APP_INFO;
    /* Parse command line */
    while ((opt = getopt(argc, argv, "c:i:p:f:t:l:o:")) != EOF) {
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
    pthread_mutex_lock(&ctx->mutex_stat);
    float avg_us = (float) stat.latency / stat.nb_packets;
    fprintf(ctx->fp, "%-8lu %-6.3f\n", stat.nb_packets, avg_us);
    stat.total_packets += stat.nb_packets;
    /* reset counter */
    stat.nb_packets = 0;
    stat.latency = 0;
    pthread_mutex_unlock(&ctx->mutex_stat);
}

void
process_pkt(u_char *arg, const struct pcap_pkthdr *header, const u_char *packet)
{
    int tv_offset = header->caplen - sizeof(struct timeval);
    struct timeval* tv = (struct timeval*)(packet + tv_offset);
    static struct timeval res;
    timersub(&header->ts, tv, &res);

    pthread_mutex_t* mutex_stat = (pthread_mutex_t *)arg;
    pthread_mutex_lock(mutex_stat);
    stat.latency += US_PER_S * res.tv_sec + res.tv_usec;
    stat.nb_packets++;
    pthread_mutex_unlock(mutex_stat);
    // print_timeval("Latency", &res);
}

void final_report(int total_sent)
{
    float lost = (total_sent - stat.total_packets) / (float)total_sent;
    fprintf(stderr, "%-10d %-10lu %-10.3f\n",
        total_sent, stat.total_packets, lost);
}

void* sniff(void *arg)
{
    struct app* app_ctx = (struct app*) arg;
    int ret;
    /* now we can set our callback function */
    ret = pcap_loop(app_ctx->sniff, app_ctx->count, process_pkt,
        (u_char*)&app_ctx->mutex_stat);
    if (ret == -1)
        fprintf(stderr, "Error pcap_loop\n");

    force_quit = 1;
    return NULL;
}

void signal_handler(int signum)
{
    if (signum == SIGINT || signum == SIGTERM) {
        printf("\n\nSignal %d received, preparing to exit...\n", signum);
        force_quit = 1;
    }
}

void* report_stat(void *arg)
{
    struct app* ctx = (struct app *)arg;
    while(!force_quit) {
        sleep(1);
        average_latency(ctx);
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

    pthread_t sniff_thread, stat_thread;

    signal(SIGTERM, signal_handler);
    signal(SIGINT, signal_handler);

    struct app app_ctx;
    app_ctx.count = config.count * count_packets(config.pcap_file);

    pcap_t *input_packets = read_pcap(config.pcap_file);

    struct bpf_program fp;    
    app_ctx.sniff = init_dev(&fp, config.interface, config.filter_exp);

    #ifdef WRITE_TO_FILE
        app_ctx.fp = fopen(config.output_fn, "w");
    #else
        app_ctx.fp = stdout;
    #endif

    if (app_ctx.fp == NULL) {
        fprintf(stderr, "Error Opening file to write\n");
        exit(EXIT_FAILURE);
    }
    pthread_mutex_init(&app_ctx.mutex_stat, NULL);

    if (pthread_create(&sniff_thread, NULL, sniff, &app_ctx) < 0) {
        fprintf(stderr, "Error creating sniff thread\n");
        exit(EXIT_FAILURE);
    }

    if (pthread_create(&stat_thread, NULL, report_stat, &app_ctx) < 0) {
        fprintf(stderr, "Error creating report thread\n");
        exit(EXIT_FAILURE);
    }

    const unsigned char *packet;
    struct pcap_pkthdr header;
    /* Now just loop through extracting packets as long as we have
     * some to read.
     */

    #define TIME_WINDOW_MS 1L
    unsigned int max_bytes_per_window = ((config.bps * TIME_WINDOW_MS) / 1000L);

    struct timespec window_start_time;

    size_t bytes_sent_in_window = 0;
    clock_gettime(CLOCK_REALTIME, &window_start_time);

    while ((packet = pcap_next(input_packets, &header)) != NULL) {
        struct timeval tv;
        size_t buflen = header.caplen + sizeof(struct timeval);
        fprintf(stderr, "packet-size %zu\n", buflen);
        unsigned char buf[buflen];
        memcpy(buf, packet, header.caplen);
        int i;
        for (i = 0 ; i < config.count; i++) {
            gettimeofday(&tv, NULL);
            memcpy(buf + header.caplen, &tv, sizeof(struct timeval));
            pcap_inject(app_ctx.sniff, buf, buflen);
            bytes_sent_in_window += buflen;

            if (bytes_sent_in_window >= max_bytes_per_window) {
                struct timespec now;
                struct timespec thresh;
                thresh.tv_sec = window_start_time.tv_sec;
                thresh.tv_nsec = window_start_time.tv_nsec;
                thresh.tv_nsec += TIME_WINDOW_MS * 1000000;
                if (thresh.tv_nsec > 1000000000L) {
                    thresh.tv_sec += 1;
                    thresh.tv_nsec -= 1000000000L;
                }
                clock_gettime(CLOCK_REALTIME, &now);
                if (now.tv_sec < thresh.tv_sec ||
                    (now.tv_sec == thresh.tv_sec && now.tv_nsec < thresh.tv_nsec)) {
                    struct timespec remaining;
                    remaining.tv_sec = thresh.tv_sec - now.tv_sec;
                    if (thresh.tv_nsec >= now.tv_nsec) {
                        remaining.tv_nsec = thresh.tv_nsec - now.tv_nsec;
                    } else {
                        remaining.tv_nsec = 1000000000L + thresh.tv_nsec - now.tv_nsec;
                        remaining.tv_sec -= 1;
                    }
                        nanosleep(&remaining, NULL);
                }
                // Reset counters and timestamp for next window
                bytes_sent_in_window = 0;
                clock_gettime(CLOCK_REALTIME, &window_start_time);
            }
        }
    }

    while(!force_quit) {
        /* wait for SIGTERM or SIGINT */
        sleep(1);
    }

    pcap_breakloop(app_ctx.sniff);

    if (pthread_join(sniff_thread, NULL)) {
        fprintf(stderr, "Error joining thread\n");
        exit(EXIT_FAILURE);
    }
    if (pthread_join(stat_thread, NULL)) {
        fprintf(stderr, "Error joining thread\n");
        exit(EXIT_FAILURE);
    }

    final_report(app_ctx.count);

    if (config.log_level == APP_DEBUG)
        printf("Cleanup\n");
    /* cleanup */
    pcap_freecode(&fp);
    pcap_close(app_ctx.sniff);
    pcap_close(input_packets);
    free_config();

    #ifdef WRITE_TO_FILE
        fclose(app_ctx.fp);
    #endif
    pthread_mutex_destroy(&app_ctx.mutex_stat);
    pthread_exit(NULL);

    return 0;
}