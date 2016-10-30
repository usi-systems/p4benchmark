#!/usr/bin/env Rscript

list.of.packages <- c("ggplot2", "tools", "reshape2", "scales", "Rmisc", "plyr")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages))
    install.packages(new.packages, repos = "http://cran.us.r-project.org",
                        dependencies = TRUE)

# library(reshape2)
# library(Rmisc)
library(plyr)
library(tools)
library(parallel)
library(ggplot2)
library(scales)

# import aggregate_latency function
source("extract_histogram.R")

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


plot_latency <- function(df) {
    pdf('set_field_latency_mean.pdf')
    ggplot(df, aes(x=variable, y=mean)) +
    geom_bar(position=position_dodge(), stat="identity") +
    geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd),
                  width=.2,                    # Width of the error bars
                  position=position_dodge(.9)) +
    theme_bw() +
    my_theme() +
    labs(x="Number of Header", y="Latency (\U00B5s) ")+
    scale_x_discrete(limits=c('1', '2', '4', '8', '16'))
}

plot_latency_99 <- function(df) {
    pdf('set_field_latency_mean_99.pdf')
    ggplot(df, aes(x=variable, y=mean_99th)) +
    geom_bar(position=position_dodge(), stat="identity") +
    geom_errorbar(aes(ymin=mean_99th-sd, ymax=mean_99th+sd),
                  width=.2,                    # Width of the error bars
                  position=position_dodge(.9)) +
    theme_bw() +
    my_theme() +
    labs(x="Number of Header", y="Latency (\U00B5s) ")+
    scale_x_discrete(limits=c('1', '2', '4', '8', '16'))
}

plot_latency_99 <- function(df) {
    pdf('parse_header.pdf')
    ggplot(df, aes(x=variable, y=mean_99th)) +
    geom_bar(position=position_dodge(), stat="identity") +
    geom_errorbar(aes(ymin=mean_99th-sd, ymax=mean_99th+sd),
                  width=.2,                    # Width of the error bars
                  position=position_dodge(.9)) +
    theme_bw() +
    my_theme() +
    labs(x="Number of Header", y="Latency (\U00B5s) ")+
    scale_x_discrete(limits=c('1', '2', '4', '8', '16'))
}

plot_lines_graph <- function(df) {
    pdf('output.pdf')
    ymax = max(df$mean_99th)
    ggplot(df, aes(x=variable)) +
    geom_line(aes(y=mean), size=1) +
    geom_line(aes(y=mean_95th), size=1) +
    geom_line(aes(y=mean_99th), size=1) +
    # geom_point(size=3, fill="white") +
    theme_bw() +
    my_theme() +
    scale_colour_hue(l=30) +
    # scale_linetype_discrete(name="Header Modification") +
    labs(x="Number of Headers", y="Latency (ns) ") +
    # theme(legend.position = c(.4, .85), legend.key.size = unit(2, "lines")) +
    theme(legend.position = "none") +
    # scale_color_grey(name="Header Modification") +
    scale_y_continuous(labels=comma, limits=c(1000, ymax))
    # scale_x_continuous(labels=comma)
    # scale_x_discrete(limits=c('1', '2', '4', '8', '16'))
}


args <- commandArgs(trailingOnly = TRUE)
dirs = list.dirs(args[1])

df <- aggregate_latency(dirs)

result <- ddply(df, c('variable', 'rate'), summarise, mean=mean(latency),
        sd=sd(latency), mean_95th=quantile(latency, c(.95)), mean_99th=quantile(latency, c(.99)))

print(result)
# plot_latency(result)
# plot_latency_99(result)
plot_lines_graph(result)

output_csv = paste(basename(args[1]), '.csv', sep='')
write.table(df, output_csv, sep=',', row.names=F, quote=F)
