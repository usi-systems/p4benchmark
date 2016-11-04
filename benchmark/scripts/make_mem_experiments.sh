#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 EXPERIMENTS_DIR"
    exit 1
else
    EXPERIMENTS_DIR=$1
fi

DONE_DIR="$EXPERIMENTS_DIR/done"
TORUN_DIR="$EXPERIMENTS_DIR/torun"
mkdir -p $DONE_DIR
mkdir -p $TORUN_DIR

pkt_count=100000
for trial in $(seq 32)
do
    for element_size in 32
    do
        #for operations in 1 2 4 8 12 16 20 24 28 32
        for registers in 1 2 4 8 12 16 20 24 28 32
        do
            #registers=1
            operations=128
            elements=128
            json_file=$(./gen_experiment.py \
                -p registers=$registers -p operations=$operations \
                -p size=$element_size -p elements=$elements -p type=mem \
                -p trial=$trial \
                -p count=$pkt_count \
                -o $TORUN_DIR)
            echo $json_file
            exp_dir=$(dirname $json_file)

            echo "#!/bin/bash" > $exp_dir/run.sh
            echo "$HOME/p4benchmark/benchmark/run_experiment.py experiment.json" >> $exp_dir/run.sh
            chmod +x $exp_dir/run.sh
        done
    done
done
