#!/usr/bin/env python

#run docking calculations, superligand and calculate descriptors

import sys, os

#drugpred_call_functions.py -db [data base] -tb [data table] -dt [result table] -user [username db] -password [password] -id [id] -prot [prot]"

drugpred_path = os.environ['DrugPred']

db = str(sys.argv[2])
tb = str(sys.argv[4])
dt = str(sys.argv[6])
us = str(sys.argv[8])
pw = str(sys.argv[10])
id = str(sys.argv[12])
prot = str(sys.argv[14])

#---------------------------------
def docking(id,prot):
	os.mkdir(id)
	os.chdir(id)
	os.mkdir('docking')
	os.chdir('docking')

	command = 'cp ../../' + prot + '.pdb' + ' .'
	print command
	os.system(command)
	#this script does the docking stuff
	command = drugpred_path + 'dp_dock.py -db ' + db + ' -tb ' + tb + ' -dt ' + dt + ' -user ' + us + ' -password '+ pw + ' -id ' + id 
	print command
	os.system(command)
	os.chdir('../..')

#---------------------------------
def superligand(id):
	os.chdir(id)
	os.chdir('docking')
	os.chdir('testing')
	os.system('gunzip res.eel1.gz')
	#calculate superligand
	command = drugpred_path + 'superligand.py' 
	print command
	os.system(command)
	os.chdir('../../..')	


#---------------------------------
def descriptors(id):
	os.chdir(id)
	os.chdir('docking')
	command = drugpred_path + 'calculate_descriptors.py -db ' + db + ' -tb ' + tb + ' -user ' + us + ' -password '+ pw + ' -id ' + id + ' -dt ' + dt
	print command
	os.system(command)
	os.chdir('../..')
#---------------------------------

#prepare for docking and dock
docking(id,prot)

#Generate superligand
superligand(id)

#calculcate descriptors
descriptors(id)

print 'finished calculations!!!!!!!!!!'

