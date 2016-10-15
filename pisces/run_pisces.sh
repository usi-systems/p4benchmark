#!/bin/bash -e

P4_INPUT_FILE=$1
OVS_PATH="$HOME/ovs"

echo $OVS_PATH
echo $P4_INPUT_FILE
echo $DPDK_BUILD

cd $OVS_PATH
sudo ./configure --with-dpdk=$DPDK_BUILD CFLAGS="-g -O2 -Wno-cast-align" \
                    p4inputfile=$P4_INPUT_FILE \
                    p4outputdir=$OVS_PATH/include/p4/src

sudo make clean
sudo make -j2

cd $OVS_PATH/ovsdb
sudo ./ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
              --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile