#!/usr/bin/env python

import argparse
from write_same_register import write_same_register
from read_same_register import read_same_register
from write_different_register import write_different_register
from read_different_register import read_different_register

def main():
    write_same_register.run()
    read_same_register.run()
    write_different_register.run()
    read_different_register.run()

if __name__=='__main__':
    main()