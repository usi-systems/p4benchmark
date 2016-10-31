#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 EXPERIMENTS_DIR"
    exit 1
else
    EXPERIMENTS_DIR=$1
fi

DONE_DIR="$EXPERIMENTS_DIR/done"
TORUN_DIR="$EXPERIMENTS_DIR/torun"

while true
do

    experiment_dirname=$(ls -rt $TORUN_DIR | head -n1)
    if [ -z $experiment_dirname ] ; then
        break
    fi

    experiment_dir="$TORUN_DIR/$experiment_dirname"
    echo $experiment_dir
    mkdir $experiment_dir/out

    (cd $experiment_dir && time ./run.sh > out/stdout 2> out/stderr)

    mv $experiment_dir $DONE_DIR
    sleep 15
done

