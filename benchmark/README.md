# dpl-benchmark

Run benchmark with Bmv2

## Setup virtual interfaces

```
sudo ./veth_setup.sh
```

## Run benchmark parser

```
python pen_parser.py
```

## Plot figure

```
./plot.R result/parser/data.csv
```