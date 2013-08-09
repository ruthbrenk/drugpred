#!/usr/bin/python

import os, sys

pdbfile = sys.argv[1]
workdir = sys.argv[2]

os.chdir(workdir)

command = '/software/naccess2.1.1/naccess ' + pdbfile
print command
os.system(command)
