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



args <- commandArgs(trailingOnly = TRUE)
plot_throughput(args[1])
plot_latency(args[2], 200000)

