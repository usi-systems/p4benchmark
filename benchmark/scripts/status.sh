#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 DIR"
    exit 1
fi
DIR=$1

ls $DIR | grep running > /dev/null
if [ $? -eq 0 ]; then
    RUNNING_DIR="$DIR/running"
    experiment_dirname=$(ls -rt $RUNNING_DIR | head -n1)
    experiment_dir="$RUNNING_DIR/$experiment_dirname"
else
    experiment_dir=$DIR
fi

stat $experiment_dir | grep Modify
stat $experiment_dir/out/results_raw.tsv | grep Modify
wc -l $experiment_dir/out/results_raw.tsv
tail $experiment_dir/out/{loss.dat,stderr,stdout}
