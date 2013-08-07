#!/usr/bin/python
#run not on cluster if openeye is not running on cluster ... :(


import os, sys, time

auri_path = sys.argv[1]
os.chdir(auri_path)

files = os.listdir('./')
files.sort()
path = os.path.abspath(os.path.curdir)
print path + ' path'
log_array = []
counter = 0
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
		print goto
		os.chdir(goto)
		command = 'rm -rf results1*'
		print command
		os.system(command)
		command = 'rm -rf acd.mdb'
		print command
		os.system(command)




		'''try:
			command = '/homes/asarkar/AgataDockingScripts3/outdock_score_subdir.py acd'
			print command
			os.system(command) 
				
		except:
			os.chdir(path)
                 	continue'''
		command = '/homes/asarkar/DrugPred2.1/outdock_score_subdir.py acd'
		print command
		os.system(command) 
		command = 'rm -Rf acd_*'
		print command
		os.system(command)
		

		os.makedirs('results12')

	

		os.chdir('results12')
		command = 'mv ../scores12.txt .'
		os.system(command)
		try:
			print os.path.curdir
			command = 'python /homes/asarkar/DrugPred2.1/getSuperlig.py scores12.txt'
			print command
			os.system(command) 
				
		except:
			os.chdir(path)
                 	continue

		os.chdir(path)	

