# dpl-benchmark

The benchmark suite contains the following applications:


|   Application   |       Features       |                                 Description                                 |
| --------------- | -------------------- | --------------------------------------------------------------------------- |
| l2-forwarding   | baseline             | Parse ethernet header and forward packets based on ethernet destination MAC |
| learning switch | clone packets        | Clone packets and send to a controller                                      |
| vlan            | add & remove headers | Tag and Untag VLAN header                                                   |
| vxlan           | MAC-in-UDP           | Encapsulates and Decapsulates an Ethernet packet in an UDP packet           |
| source routing  | recursive parsing    | Parse N nested headers                                                      |
| nat             | table size           | Dynamically add table entries                                               |
|                 |                      |                                                                             |
