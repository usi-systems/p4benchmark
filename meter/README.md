# Meters

## Description

This application simply demonstrates two-rate three-color Mark (trTCM) policy
using P4 meters. The meter policy is configured to rate-limit traffic to a 
bandwidth limit of 1 KBps and a burst-size limit of 128 Bytes for green 
traffic. It also is configured to a peak bandwidth limit of 5 KBps and a peak 
burst-size limit of 256 Bytes for yellow traffic.

## Running Demo

We provide a small demo to let you test the program.

- [run_switch.sh](run_switch.sh): compile the P4 program and starts the switch,
  also configures the data plane by running the CLI [commands](commands.txt)
- [send_and_receive.py](send_and_receive.py): send and receive packets

To run the demo:
- create virtual interfaces (need to run only if the VM has restarted): 
`sudo ../veth_setup.sh`
- start the switch: `sudo ./run_switch.sh`


## Sending Rate
Each packet is 64B in size. You can adjust the inter-packet by option `-t`

### Example 1: Send 10 packets per second ~ (10 packets * 64 B/packet) = 640 B/s

- `sudo ./send_and_receive.py -c 100 -t 0.1`

Because the throughput is below the first rate ( 1KB/s ), then all packets are
marked as green traffic which are then forwarded to port 1 (interface: `veth2`).


### Example 2: Send 15 packets per second ~ (16 packets * 64 B/packet) = 1024 B/s

- `sudo ./send_and_receive.py -c 100 -t 0.06`

The throughput fluctuates around the first rate ( 1KB/s ), then most of packets are
marked as yellow traffic which are then forwarded to port 2 (interface: `veth4`).


### Example 2: Send 1000 packets per second ~ (1000 packets * 64 B/packet) > 5 KB/s

note: the software cannot send packets with precisely inter-gaps. Then it's safer
to minimize the inter-gaps for reaching the peak throughput.

- `sudo ./send_and_receive.py -c 1000 -t 0.001`

The throughput reached the peak rate ( 5 KB/s ), then most of packets are
marked as red traffic which are then drop.

