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

    read_pcap(argv[1]);

    if (argc < 4) {
        print_app_usage(argv[0]);
        exit(EXIT_SUCCESS);
    }

    capture(argv[2], argv[3]);

    return 0;
}