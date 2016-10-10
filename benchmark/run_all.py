#!/usr/bin/env python

import pen_parser
import pen_pipeline
import pen_memory
import pen_packet_mod

def main():
    pen_parser.main()
    pen_pipeline.main()
    pen_memory.main()
    pen_packet_mod.main()

if __name__=='__main__':
    main()