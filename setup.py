import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "P4 Benchmark project",
    version = "0.0.1",
    author = "Huynh Tu Dang",
    author_email = "huynh.tu.dang@usi.ch",
    description = ("A tool for generating P4 programs which test various "
                                   "aspect of P4 compilers and targets."),
    license = "BSD",
    keywords = "P4 benchmark",
    url = "https://github.com/usi-systems/p4benchmark",
    packages = ['p4gen', 'action_complexity', 'packet_modification', 'parsing',
                'processing', 'state_access', 'tests'],
    package_dir = {'p4gen' : 'p4gen'},
    package_data = {'p4gen' : ['template/*/*']},
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Topic :: Benchmark",
        "License :: OSI Approved :: BSD License",
    ],
)