#!/usr/bin/Rscript

options(warn=1)
args <- commandArgs(trailingOnly = TRUE)

dirs = list.dirs(args[1])


read_latency <- function(file_path, variable, offer_load, packet_lost) {
    df <- read.csv(file_path, sep='', header=FALSE, col.names=c('throughput', 'latency'))
    # cut the first and the last five rows
    df <- tail(df,-5)
    df <- head(df,-5)
    df$variable <- as.numeric(variable)
    df$offer_load <- as.numeric(offer_load)
    df$packet_lost <- as.numeric(packet_lost)
    # data <- apply(df, 2, mean)
    # print(typeof(data))
    # return (data)
    return (df)
}

has_packet_lost <- function(file_path) {
    cmd = sprintf("gawk 'END {print}' %s", file_path)
    res = system(cmd, intern = TRUE)
    data = strsplit(res, '\\s+')
    sent = as.numeric(data[[1]][1])
    received = as.numeric(data[[1]][2])
    return (received < sent)
}


dfs = data.frame(throughput=numeric(0), latency=numeric(0), offer_load=numeric(0),
                variable=numeric(0), packet_lost=logical(0))

for (d in dirs) {
    latency_path = list.files(d, pattern='latency.csv', full.names=TRUE)
    loss_path = list.files(d, pattern='loss.csv', full.names=TRUE)
    if ((length(latency_path) != 0)) {

    }
    if ((length(latency_path) != 0)) {
        offer_load <- basename(d)
        variable <- basename(dirname(d))
        packet_lost = has_packet_lost(loss_path)
        df <- read_latency(latency_path, variable, offer_load, packet_lost)
        dfs <- rbind(df, dfs)

    }
}

# Find mean throughput and latency
mydf <-aggregate(dfs[1:2], by=list(var=dfs$variable, load=dfs$offer_load,
                lost=dfs$packet_lost), FUN=mean)

# Find maximum throughput
final <-aggregate(mydf[4:5], by=list(var=mydf$var, lost=mydf$lost), FUN=max)
print(final)