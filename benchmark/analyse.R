#!/usr/bin/Rscript

options(warn=1)
args <- commandArgs(trailingOnly = TRUE)

dirs = list.dirs(args[1])


read_latency <- function(file_path, variable, offer_load) {
    df <- read.csv(file_path, sep='', header=FALSE, col.names=c('throughput', 'latency'))
    # cut the first and the last five rows
    df <- tail(df,-5)
    df <- head(df,-5)
    df$variable <- as.numeric(variable)
    df$offer_load <- as.numeric(offer_load)
    # data <- apply(df, 2, mean)
    # print(typeof(data))
    # return (data)
    return (df)
}

dfs = data.frame(throughput=numeric(0), latency=numeric(0), offer_load=numeric(0),
                variable=numeric(0))

for (d in dirs) {
    latency_path = list.files(d, pattern='latency.csv', full.names=TRUE)
    loss_path = list.files(d, pattern='loss.csv', full.names=TRUE)
    if ((length(latency_path) != 0)) {
        offer_load <- basename(d)
        variable <- basename(dirname(d))
        df <- read_latency(latency_path, variable, offer_load)
        dfs <- rbind(df, dfs)
    }
}

print(dfs)
aggdata <-aggregate(dfs[,1:2], by=list(dfs$variable, dfs$offer_load), FUN=mean)
print(aggdata)


