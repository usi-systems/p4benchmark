#!/usr/bin/Rscript

list.of.packages <- c("ggplot2", "tools", "reshape2", "scales", "Rmisc", "plyr")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages))
    install.packages(new.packages, repos = "http://cran.us.r-project.org",
                        dependencies = TRUE)

library(ggplot2)
library(tools)
library(reshape2)
library(scales)
library(Rmisc)
library(plyr)

options(warn=1)

my_theme <- function() {
    theme(panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank(),
        text = element_text(size=34, family='Times'),
        axis.title.y=element_text(margin=margin(0,10,0,0)),
        axis.title.x=element_text(margin=margin(10,0,0,0)),
        legend.text = element_text(size=30, family='Times'),
        legend.position = c(.8, .6)
    )
}

plot_throughput <- function(input) {
    df <- read.csv(input, header=TRUE, sep="")
    tpdf <- df[df$lost==0,]
    print(tpdf)
    pdf('throughput.pdf')
    ggplot(tpdf, aes(x=var, y=throughput)) +
    geom_line() +
    labs(x="Number of Headers", y="Throughput (Pkts / S) ")+
    theme_bw() +
    my_theme() +
    scale_y_continuous(labels=comma) +
    scale_x_continuous(labels=comma, breaks=pretty_breaks(n = 8))
}

plot_latency <- function(input, at_throughput) {
    df <- read.csv(input, header=TRUE, sep="")
    data <- df[df$load==at_throughput,]
    print(data)
    pdf('latency.pdf')
    ggplot(data, aes(x=var, y=latency)) +
    geom_line() +
    labs(x="Number of Headers", y="Latency (\U00B5s) ")+
    theme_bw() +
    my_theme() +
    scale_y_continuous(labels=comma) +
    scale_x_continuous(labels=comma, breaks=pretty_breaks(n = 8))
}

plot_latency_all <- function(input) {
    df <- read.csv(input, header=TRUE, sep="")
    print(df)
    df$load <- df$load / 100000
    pdf('latency.pdf')
    ggplot(df, aes(x=load, y=latency)) +
    geom_line() +
    # facet_grid(. ~ load, scales='free', space='free') +
    labs(x="Number of Headers", y="Latency (\U00B5s) ")+
    theme_bw() +
    my_theme() +
    scale_y_continuous(labels=comma) +
    scale_x_continuous(labels=comma, breaks=pretty_breaks(n = 8))
}

plot_latency_cdf <- function(input) {
    df <- read.csv(input, header=TRUE, sep="", , colClasses=c('numeric', 'numeric', 'numeric', 'numeric', 'numeric'))
    # df$offer_load <- df$offer_load * 8 / 1000000
    df <- df[df$packet_lost == 0,]
    # df <- df[df$offer_load == 500000,]
    pdf('cdf_latency.pdf')
    # df <- ddply(df, c('variable', 'offer_load', 'packet_lost'), summarise, latency=quantile(latency, c(.99)))
    print(df)
    ggplot(df, aes(x=latency, colour=factor(offer_load))) +
    stat_ecdf(aes(linetype=factor(offer_load), colour=factor(offer_load))) +
    facet_grid(. ~ variable) +
    theme_bw()
}

plot_latency_percentile <- function(input) {
    df <- read.csv(input, header=TRUE, sep="", , colClasses=c('numeric', 'numeric', 'numeric', 'numeric', 'numeric'))
    df$offer_load <- df$offer_load * 8 / 1000000
    df <- df[df$packet_lost == 0,]
    # df <- df[df$offer_load == 500000,]
    pdf('cdf_latency.pdf')
    df <- ddply(df, c('variable', 'offer_load', 'packet_lost'), summarise, latency=quantile(latency, c(.99)))
    print(df)
    ggplot(df, aes(x=offer_load, y=latency, colour=factor(variable))) +
    geom_line() +
    theme_bw() +
    my_theme() +
    theme(legend.position = "none")
}


args <- commandArgs(trailingOnly = TRUE)
# plot_throughput(args[1])
# plot_latency(args[2], 200000)

# plot_latency_all(args[1])
# plot_latency_cdf(args[1])
plot_latency_percentile(args[1])