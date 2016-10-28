#!/usr/bin/Rscript

# library(reshape2)
# library(scales)
# library(Rmisc)
library(plyr)
library(tools)
library(parallel)
library(ggplot2)

get_latency <- function(input) {
    rate <- basename(dirname(input))
    run_nth <- basename(dirname(dirname(input)))
    variable <- basename(dirname(dirname(dirname(input))))
    df <- read.csv(input, col.names=c('latency', 'count'), colClasses=c('numeric', 'numeric'))

    latency <- rep(df$latency, df$count)
    q <- quantile(latency, c(.95, .99))
    mean <- mean(latency)
    sd <- sd(latency)
    df = data.frame(run_nth=run_nth, variable=variable, rate=rate, mean_lat=mean, sd_lat=sd, q95th=q[[1]], q99th=q[[2]])
    return (df)
}

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
    df$mean <- df$mean / 1000
    df$sd <- df$sd / 1000
    pdf('set_field_latency.pdf')
    ggplot(df, aes(x=variable, y=mean)) +
    geom_bar(position=position_dodge(), stat="identity") +
    geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd),
                  width=.2,                    # Width of the error bars
                  position=position_dodge(.9)) +
    theme_bw() +
    my_theme() +
    labs(x="Number of Set-Field Actions", y="Latency (\U00B5s) ")+
    scale_x_discrete(limits=c('1', '2', '4', '8', '16', '32', '64'))

}

args <- commandArgs(trailingOnly = TRUE)
dirs = list.dirs(args[1])

# Initial a vector
histogram_files <- vector()

for (d in dirs) {
    histogram_path = list.files(d, pattern='histogram.csv', full.names=TRUE)
    if ((length(histogram_path) != 0)) {
        histogram_files <- append(histogram_files, histogram_path)
    }
}


no_cores <- detectCores() - 1

dfs = mclapply(histogram_files, get_latency, mc.cores=no_cores)
df <- NULL
for (i in (dfs)) {
    df <- rbind(df, i)
}

result <- ddply(df, c('variable', 'rate'), summarise, mean=mean(mean_lat), sd=sd(sd_lat), mean_95th=mean(q95th), mean_99th=mean(q99th))

print(result)
plot_latency(result)
