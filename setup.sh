#!/bin/bash

git submodule init
git submodule update

cd behavioral-model
./autogen.sh
./configure
sudo make

cd ../p4c-bm
sudo pip install -r requirements.txt
sudo pip install -r requirements_v1_1.txt
sudo python setup.py install

cd ..