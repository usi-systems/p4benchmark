#!/bin/bash

DIR=utilities

$DIR/ovs-vsctl del-br br0
$DIR/ovs-vsctl --no-wait init
$DIR/ovs-vsctl add-br br0 -- set bridge br0 datapath_type=netdev
$DIR/ovs-vsctl set bridge br0 protocols=OpenFlow15
$DIR/ovs-vsctl add-port br0 dpdk0 -- set Interface dpdk0 type=dpdk
$DIR/ovs-vsctl add-port br0 dpdk1 -- set Interface dpdk1 type=dpdk
