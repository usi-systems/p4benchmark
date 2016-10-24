#!/bin/bash

DIR="p4benchmark_sdnet"
mkdir -p $DIR
mkdir -p $DIR/"add_header"
mkdir -p $DIR/"remove_header"

for i in 1 2 4 8 16
do
    python ../generate_p4_program.py --mod-packet --mod-type add --fields 4 --headers $i
    mv output $DIR/add_header/$i
    python ../generate_p4_program.py --mod-packet --mod-type rm --fields 4 --headers $i
    mv output $DIR/remove_header/$i
done

tar -cvf ${DIR}.tar.gz $DIR