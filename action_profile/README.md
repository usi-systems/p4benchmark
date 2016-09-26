# Action Profile

## Description

This example gives a skeleton ECMP implementation, using an action profile. A P4
action profile is mapped to an indirect table in bmv2. More precisely, in our
case, the P4 objects `ecmp_group` and `ecmp_action_profile` are mapped to one
bmv2 indirect match table. This has the limitation that sharing action profiles
between P4 tables is not supported in bmv2.

### Running the demo

As always, you can start the switch with `./run_switch.sh` (and wait until
`READY` is displayed). We program the dataplane with the following CLI commands
(from [commands.txt] (commands.txt)):

```
01. table_indirect_create_group ecmp_group
02. table_indirect_create_member ecmp_group _nop
03. table_indirect_create_member ecmp_group set_ecmp_nexthop 1
04. table_indirect_create_member ecmp_group set_ecmp_nexthop 2
05. table_indirect_create_member ecmp_group set_ecmp_nexthop 3
06. table_indirect_add_member_to_group ecmp_group 1 0
07. table_indirect_add_member_to_group ecmp_group 3 0
08. table_indirect_set_default ecmp_group 0
09. table_indirect_add_with_group ecmp_group 10.0.0.1 => 0
10. table_dump ecmp_group
```

These commands do the following:

01. create a group, which receives group handle 0
02. create a member with action _nop and no action data (member handle 0)
03. create a member with action set_ecmp_nexthop and action data port=1 (member handle 1)
04. create a member with action set_ecmp_nexthop and action data port=2 (member handle 2)
05. create a member with action set_ecmp_nexthop and action data port=3 (member handle 3)
06. add member 1 to group 0
07. add member 3 to group 0
08. set member 0 (_nop) has the default for table ecmp_group
09. add an entry to table ecmp_group, which maps destination IPv4 address
    10.0.0.1 to group 0 (which includes members 1 and 3)
10. simply dump the table

These commands are sent automatically when you run `./run_switch.sh`. The last
command should display the following information:

```
ecmp_group:
0: 0a000001 => group(0)
members:
0: _nop - 
1: set_ecmp_nexthop - 1,
2: set_ecmp_nexthop - 2,
3: set_ecmp_nexthop - 3,
4: set_ecmp_nexthop - 4,
groups:
0: { 1, 3, }
```

When we send a packet to the switch (on any port) with destination address
10.0.0.1, the egress port will be set to either 1 or 3. This is because we only
added members 1 and 3 to the group. Which port / member is used for a given
packet is determined by computing a hash over the IP source address and the IP
protocol number. See the P4 program for more details.

After starting the switch, run `sudo python send_and_count.py`. This Python
script will send 200 packets to the switch and count the pakcets coming out of
ports 2 and 3. The two numbers should be almost the same:

```
Sending 200 packets on port 0
port 1: 106 packets (53%)
port 2: 0 packets (0%)
port 3: 94 packets (47%)
port 4: 0 packets (0%)
```
