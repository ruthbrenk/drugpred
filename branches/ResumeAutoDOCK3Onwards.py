#!/usr/bin/python
import os, sys, os.path, time

db = sys.argv[1]
datatable = sys.argv[2]
desctable = sys.argv[3]
uname = sys.argv[4]
password = sys.argv[5]
curr_dir = os.path.abspath('./')


### RUN AGATA'S AUTODOCK_CLUSTER3 ###
command = 'qsub /homes/asarkar/AgataDockingScripts3/autoDock_cluster3.py' + ' ' + curr_dir
os.system(command)

### wait for qsubbed jobs to finish ###

command = 'qstat -u '+uname+'  > log_cluster.txt'
os.system(command)

log_cluster = open('log_cluster.txt', 'r').readlines()
#print log_cluster
while len(log_cluster) !=0:
	command = 'qstat -u '+uname+'  > log_cluster.txt'
	os.system(command)
	log_cluster = open('log_cluster.txt', 'r').readlines()
	#print log_cluster
	time.sleep(1)


### COPY ALL PROTEIN AND SUPERLIGAND FILES TO $PATH ###


command = '/homes/asarkar/DrugPred2.0/CalculateDescriptors.py ' + curr_dir + ' ' + ' ' + db + ' ' + datatable + ' ' + desctable + ' ' + uname + ' ' + password
os.system(command)
