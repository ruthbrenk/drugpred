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

files = os.listdir('./')
files.sort()
path = os.path.abspath(os.path.curdir)
log_array = []
counter = 0
username = str(sys.argv[1])
for file_ in files:
        if file_[-4:] == '.pdb':
		os.chdir(path)
		pdb_code = file_[:-4]
		os.chdir(pdb_code)	# cd in new directory and do docking stuff
		os.chdir('docking')
		#but first copy the right pdb file in dir
		#command= 'mv ../' + file_ + ' .'

		#DOCKING!!!
		#cd testing and run dock_vol.test but first copy right INDOCK file in testing
		goto= path + '/' + pdb_code + '/docking/testing'
		os.chdir(goto)
		command = 'rm -f INDOCK'
		os.system(command)
		command = 'cp /homes/asarkar/DrugPred2.1/INDOCK_cluster INDOCK'
		os.system(command)

		command = '/homes/asarkar/DrugPred2.1/cl_startdock.py /homes/asarkar/AgataDockingScripts/new_dbs_test/ False'
		os.system(command)	
		

		# if file exists check time!!!		
		command = 'qstat -u '+username+'  > log_cluster.txt'
		os.system(command)
	
		log_cluster = open('log_cluster.txt', 'r').readlines()
		#print log_cluster
		while len(log_cluster) >= 1000:
			command = 'qstat -u '+username+'  > log_cluster.txt'
			os.system(command)
			log_cluster = open('log_cluster.txt', 'r').readlines()
			#print log_cluster
			time.sleep(1)

		os.chdir(path)	

command = "find . -name 'start_dock.bin.*' -exec rm -f {} \;"
os.system(command)
