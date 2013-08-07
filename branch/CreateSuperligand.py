#!/usr/bin/python
import os, sys, time

username = sys.argv[1]

path = os.path.abspath(os.path.curdir)

command = 'qstat -u '+username+'  > log_cluster.txt'
os.system(command)
log_cluster = open('log_cluster.txt', 'r').readlines()

while len(log_cluster) >= 1000:
	command = 'qstat -u '+username+'  > log_cluster.txt'
	os.system(command)
	log_cluster = open('log_cluster.txt', 'r').readlines()
	#print log_cluster
	time.sleep(1)

### RUN AGATA'S AUTODOCK_CLUSTER3 ###
command = 'qsub -V -cwd /homes/asarkar/DrugPred2.1/autoDock_cluster3.py ' + path
os.system(command)

command = "find . -name 'autoDock_cluster3.py.*' -exec rm -f {} \;"
os.system(command)
