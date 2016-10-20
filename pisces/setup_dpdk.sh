#!/bin/bash -e

PORT1=${1-"eth1"}
PORT2=${2-"eth2"}

sudo modprobe uio
sudo insmod $RTE_SDK/$RTE_TARGET/kmod/igb_uio.ko
sudo insmod $RTE_SDK/$RTE_TARGET/kmod/rte_kni.ko "lo_mode=lo_mode_ring"

# Add PORT1 and PORT2 interfaces to DPDK
sudo ifconfig $PORT1 down
sudo $RTE_SDK/tools/dpdk_nic_bind.py -b igb_uio $PORT1
sudo ifconfig $PORT2 down
sudo $RTE_SDK/tools/dpdk_nic_bind.py -b igb_uio $PORT2

# To view these interfaces run the following command:
$RTE_SDK/tools/dpdk_nic_bind.py --status

# Configure Huge Pages
sudo mkdir -p /mnt/huge
(mount | grep hugetlbfs) > /dev/null || sudo mount -t hugetlbfs nodev /mnt/huge
sudo bash -c 'echo 1024 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages'
