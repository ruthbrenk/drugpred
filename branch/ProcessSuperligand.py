#!/usr/bin/python
import os, sys, time

db = sys.argv[1]
datatable = sys.argv[2]
desctable = sys.argv[3]
uname = sys.argv[4]
password = sys.argv[5]
pacode = sys.argv[6]
wantedpdb = sys.argv[7]
wantedlig = sys.argv[8]
curr_dir = os.path.abspath('./')

path = os.path.abspath(os.path.curdir)



### wait for qsubbed jobs to finish ###

command = 'qstat -u '+uname+'  > log_cluster.txt'
os.system(command)

log_cluster = open('log_cluster.txt', 'r').readlines()
#print log_cluster
while len(log_cluster) >= 1000:
	command = 'qstat -u '+uname+'  > log_cluster.txt'
	os.system(command)
	log_cluster = open('log_cluster.txt', 'r').readlines()
	#print log_cluster
	time.sleep(1)


### COPY ALL PROTEIN AND SUPERLIGAND FILES TO $PATH ###


command = 'qsub -V -cwd /homes/asarkar/DrugPred2.1/CalculateDescriptors.py ' + curr_dir + ' ' + db + ' ' + datatable + ' ' + desctable + ' ' + uname + ' ' + password + ' ' + pacode + ' ' + wantedpdb + ' ' + wantedlig
os.system(command)

command = "find . -name 'CalculateDescriptors.py.*' -exec rm -f {} \;"
os.system(command)