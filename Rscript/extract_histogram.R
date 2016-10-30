#!/usr/bin/env Rscript

list.of.packages <- c("parallel")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages))
    install.packages(new.packages, repos = "http://cran.us.r-project.org",
                        dependencies = TRUE)

library(parallel)

get_latency <- function(input) {
    rate <- basename(dirname(input))
    run_nth <- basename(dirname(dirname(input)))
    variable <- as.numeric(basename(dirname(dirname(dirname(input)))))
    df <- read.csv(input, col.names=c('latency', 'count'), colClasses=c('numeric', 'numeric'))

    latency <- rep(df$latency, df$count)
    df = data.frame(run_nth=run_nth, variable=variable, rate=rate, latency=latency)
    return (df)
}

aggregate_latency <- function(dirs) {
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
    return(df)
}

args <- commandArgs(trailingOnly = TRUE)
dirs = list.dirs(args[1])

df <- aggregate_latency(dirs)
print(summary(df))
# result <- ddply(df, c('variable', 'rate'), summarise, mean=mean(latency), sd=sd(latency), percentile99=quantile(latency, c(.99)))
# print(result)

# output_csv = paste(basename(args[1]), '.csv', sep='')
# write.table(df, output_csv, sep=',', row.names=F, quote=F)
