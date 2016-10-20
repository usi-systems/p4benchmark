#!/bin/bash -e

sudo apt-get update
sudo apt-get install -y --reinstall python-pkg-resources

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

git clone https://github.com/p4lang/p4-hlir.git
cd p4-hlir/
sudo python setup.py install

cd $DIR
git clone https://github.com/P4-vSwitch/p4c-behavioral.git
cd p4c-behavioral/
git checkout ovs
sudo python setup.py install

cd $DIR
git clone https://github.com/P4-vSwitch/ovs.git
cd ovs/
git checkout p4
git submodule update --init

# Build DPDK

cd $DIR/ovs/deps/dpdk
patch -p1 -N < ../../setup-scripts/patches/dpdk.patch
make -j 2 install T=x86_64-native-linuxapp-gcc


# Configure Huge Pages

sudo mkdir -p /mnt/huge
(mount | grep hugetlbfs) > /dev/null || sudo mount -t hugetlbfs nodev /mnt/huge
sudo bash -c 'echo 1024 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages'
#sudo bash -c 'echo 1024 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages'


#Setup DPDK-specific environment variables
export RTE_SDK=$DIR/ovs/deps/dpdk
export RTE_TARGET=x86_64-native-linuxapp-gcc
export DPDK_DIR=$RTE_SDK
export DPDK_BUILD=$DPDK_DIR/$RTE_TARGET/

cat > $HOME/.piscesrc <<- EOM
export RTE_SDK=$DIR/ovs/deps/dpdk
export RTE_TARGET=x86_64-native-linuxapp-gcc
export DPDK_DIR=\$RTE_SDK
export DPDK_BUILD=\$DPDK_DIR/\$RTE_TARGET/

EOM
cat >> $HOME/.bashrc <<- EOM
source ~/.piscesrc
EOM


# Build ovs p4
cd $DIR/ovs
./boot.sh
./configure --with-dpdk=$DPDK_BUILD CFLAGS="-g -O2 -Wno-cast-align" \
            p4inputfile=./include/p4/examples/l2_switch/l2_switch.p4 \
            p4outputdir=./include/p4/src
make -j 2

# Create OVS database files and folders
sudo mkdir -p /usr/local/etc/openvswitch
sudo mkdir -p /usr/local/var/run/openvswitch
cd $DIR/ovs/ovsdb/
sudo ./ovsdb-tool create /usr/local/etc/openvswitch/conf.db ../vswitchd/vswitch.ovsschema


# Setup DPDK kernel modules
# source bind_nics.sh