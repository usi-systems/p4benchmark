#!/usr/bin/env python

import argparse

from headers import headers
from fields import fields
from branches import branches

if __name__=='__main__':
    headers.run()
    fields.run()
    branches.run()