Action Profile
==============

This example gives a skeleton ECMP implementation, using an action profile. A P4
action profile is mapped to an indirect table in bmv2. More precisely, in our
case, the P4 objects `ecmp_group` and `ecmp_action_profile` are mapped to one
bmv2 indirect match table. This has the limitation that sharing action profiles
between P4 tables is not supported in bmv2.

Running the demo
----------------

As always, you can start the switch with `./run_switch.sh` (and wait until
`READY` is displayed). We program the data plane with the following CLI commands
(from commands.txt)::

    table_indirect_create_group ecmp_group
    table_indirect_create_member ecmp_group _nop
    table_indirect_create_member ecmp_group set_ecmp_nexthop 1
    table_indirect_create_member ecmp_group set_ecmp_nexthop 2
    table_indirect_create_member ecmp_group set_ecmp_nexthop 3
    table_indirect_add_member_to_group ecmp_group 1 0
    table_indirect_add_member_to_group ecmp_group 3 0
    table_indirect_set_default ecmp_group 0
    table_indirect_add_with_group ecmp_group 10.0.0.1 => 0
    table_dump ecmp_group

These commands do the following:

1. create a group, which receives group handle 0
2. create a member with action _nop and no action data (member handle 0)
3. create a member with action set_ecmp_nexthop and action data port=1 (member handle 1)
4. create a member with action set_ecmp_nexthop and action data port=2 (member handle 2)
5. create a member with action set_ecmp_nexthop and action data port=3 (member handle 3)
6. add member 1 to group 0
7. add member 3 to group 0
8. set member 0 (_nop) has the default for table ecmp_group
9. add an entry to table ecmp_group, which maps destination IPv4 address
   10.0.0.1 to group 0 (which includes members 1 and 3)
10. simply dump the table

These commands are sent automatically when you run `./run_switch.sh`. The last
command should display the following information::

    ecmp_group:
    0: 0a000001 => group(0)
    members:
    0: _nop - 
    1: set_ecmp_nexthop - 1,
    2: set_ecmp_nexthop - 2,
    3: set_ecmp_nexthop - 3,
    groups:
    0: { 1, 3, }

When we send a packet to the switch (on any port) with destination address
10.0.0.1, the egress port will be set to either 1 or 3. This is because we only
added members 1 and 3 to the group. Which port / member is used for a given
packet is determined by computing a hash over the IP source address, IP destination
address, and the IP protocol number. See the P4 program for more details.

After starting the switch, run `sudo python send_and_count.py`. This Python
script will send 500 packets to the switch and count the packets coming out of
ports 2 and 3. The two numbers should be almost the same::

    Sending 500 packets on port 0
    port 1: 269 packets (53%)
    port 2: 0 packets (0%)
    port 3: 231 packets (47%)
    port 4: 0 packets (0%)
