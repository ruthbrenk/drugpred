#!/usr/bin/env python

#master script to run DrugPred


#setup directory for each drugpred job
#prepare for docking
#dock
#receptors: must be called 'prot'.pdb


import sys, mysql, os

#*******************************************************************************
# MAIN help
#**********
#

outhelp = 0
if len(sys.argv) == 2 and sys.argv[1] == "--help":
	outhelp = 1
elif len(sys.argv) != 13:
	outhelp = 1
elif sys.argv[1] != "-db" or sys.argv[3] != "-tb" or sys.argv[5] != "-dt" or sys.argv[7]  != "-user"  or sys.argv[9] != "-password" or sys.argv[11] != "-cluster": 
	outhelp = 1


if outhelp == 1:
	print "*** Script to set protein atoms to C and write in new file, adds cofactor to new file, writes ligand into xtal-lig.pdb, connects to the db to get ligand and cofactor information ***\n"
	print "Written by Agata Krasowski *a.krasowski@dundee.ac.uk*\n"
	print "Usage:   --help shows this help"
	print "         -db [data base] -tb [data table] -dt [result table] -user [username db] -password [password] -cluster [True|False]"

	sys.exit()

#*******************************************************************************
# MAIN
#***************

drugpred_path = os.environ['DrugPred']
print drugpred_path


db = str(sys.argv[2])
tb = str(sys.argv[4])
dt = str(sys.argv[6])
us = str(sys.argv[8])
pw = str(sys.argv[10])
if str(sys.argv[12]) == 'True':
	cluster = True
elif str(sys.argv[12]) == 'False':
	cluster = False
else:
	print "Wrong argument for cluster: True|False"
	sys.exit()


#check that db values are okay
#tables
conn=mysql.connect2server(pw, us, db)  			    
cursor = conn.cursor ()

tables = [tb, dt]

for table in tables:
	command = 'SHOW TABLES LIKE "' + table +'"'
	#print command
	cursor.execute(command)
	rows = cursor.fetchall()
	if len(rows) ==0:
		print 'Table does not exist: ', table
		sys.exit()
#fields
fields = ['id', 'prot', 'to_do']
for field in fields:
	command = 'SHOW COLUMNS FROM ' + tb + ' LIKE "' + field + '"'
	#print command
	cursor.execute(command)
	rows = cursor.fetchall()
	if len(rows) ==0:
		print 'Field', field, ' does not exist in table', tb
		sys.exit()

#check environment variables

if not os.environ.get('DockingScripts'):
	print 'environment variable DockingScripts is not set'
	sys.exit()
elif not os.environ.get('DrugPred'):
	print 'environment variable DockingScripts is not set'
        sys.exit()



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
	command = drugpred_path + 'dp_dock.py -db ' + db + ' -tb ' + tb + ' -user ' + us + ' -password '+ pw + ' -id ' + id 
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

#get to do from table

command = "select id, prot from " + tb + " where to_do is Null"
print command
cursor.execute(command)
rows = cursor.fetchall ()
conn.close()

if not cluster:

   for fields in rows:
	id = fields[0]
	prot = fields[1]

	command = drugpred_path + 'drugpred_call_functions.py -db ' + db + ' -tb ' + tb + ' -dt ' + dt  + ' -user ' + us + ' -password '+ pw + ' -id ' + id +  ' -prot ' + prot
	print command
	os.system(command)



else:
   for fields in rows:
	id = fields[0]
	prot = fields[1]
	print 'submit job on cluster'
	
	file_name = id + '_' + prot + '_start.bin'
	start_file = open(file_name, 'w')
	start_file.write("#BSUB-q short             	# Job queue\n#BSUB-o job.output              # output is sent to file job.output\n#BSUB-J test_mogon              # name of the job\n")
	start_file.write(drugpred_path + 'drugpred_call_functions.py -db ' + db + ' -tb ' + tb + ' -dt ' + dt  + ' -user ' + us + ' -password '+ pw + ' -id ' + id +  ' -prot ' + prot + '\n')
	start_file.close()

	os.system('chmod 744 '  + file_name)
	command = 'qsub -q short -lm 500000000000 ' + file_name
	print command
	os.system(command)



print 'done!!!!!!!!!!!!!'

#to do:
#check with bigger super ligand if I get about the same descriptors
#optimize docking setup
#make ready for cluster
#redock test set
#dock RNA molecules
#analyse
#write paper








