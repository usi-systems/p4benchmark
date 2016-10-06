#!/bin/bash

sudo apt-get update -y

sudo apt-get install -y git autoconf python-pip build-essential python-dev

git submodule init
git submodule update

cd behavioral-model
sudo ./install_deps.sh
./autogen.sh
./configure
sudo make

cd ../p4c-bm
sudo pip install -r requirements.txt
sudo pip install -r requirements_v1_1.txt
sudo python setup.py install

cd ..
sudo pip install -r requirements.txt
sudo ./veth_setup.sh

cd pktgen
mkdir build
cd build
cmake ..
make

cd ../..