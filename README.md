# dpl-benchmark

The benchmark suite contains the following applications:


|   Application   |        Features       |                                 Description                                 |
| --------------- | --------------------- | --------------------------------------------------------------------------- |
| l2-forwarding   | baseline              | Parse ethernet header and forward packets based on ethernet destination MAC |
| learning switch | clone packets         | Clone packets and send to a controller                                      |
| vlan            | add & remove headers  | Tag and Untag VLAN header                                                   |
| vxlan           | MAC-in-UDP            | Encapsulates and Decapsulates an Ethernet packet in an UDP packet           |
| source routing  | recursive parsing     | Parse N nested headers                                                      |
| nat             | table size            | Dynamically add table entries                                               |
| mpls            | push, pop headers     | Push or Pop MPLS labels                                                     |
| n_tables        | go through pipelines  | Pass packets through a varying length of pipelines                          |
| state_access    | read & write register | Write to one element or Read from a range of register elements              |
|                 |                       |                                                                             |

## How to install?
Simply run:
```
sudo ./setup.sh
```