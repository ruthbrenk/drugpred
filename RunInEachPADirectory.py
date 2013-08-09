#!/usr/bin/python
import os, sys, time

# Find all PA directories in current directory and subdirectories
# that contain PDB files (format is: PAxxxx_PDBx_LIG)


files = os.listdir('./')
files.sort()
path = os.path.abspath(os.path.curdir)

db = str(sys.argv[1])
datatable = str(sys.argv[2])
desctable = str(sys.argv[3])
uname = str(sys.argv[4])
password = str(sys.argv[5])

tot_pdbs = 0
for file in files:
	if not os.path.isdir(file) or file[:2] <> 'PA' or len(file) > 6:
		continue
	pacode = file
	print pacode
	os.chdir(file)
	xfiles = os.listdir('./')
	for xfile in xfiles:
		if not os.path.isdir(xfile) or len(xfile.split('_')) <> 3:
			continue
		else:
			print xfile
			xpacode,pdbcode,ligand = xfile.split('_')
			tot_pdbs += 1
			os.chdir(xfile)
			command = '/homes/asarkar/DrugPred2.1/PrepareForDocking.py ' + db + ' ' + datatable + ' ' + desctable + ' ' + uname + ' ' + password + ' ' + pacode + ' ' + pdbcode + ' ' + ligand
			print command
			os.system(command)
			os.chdir('../')
			
			command = 'qstat -u '+uname+'  > log_cluster.txt'
			os.system(command)
			log_cluster = open('log_cluster.txt', 'r').readlines()
			#print log_cluster
			while len(log_cluster) > 102:
				command = 'qstat -u '+uname+'  > log_cluster.txt'
				os.system(command)
				log_cluster = open('log_cluster.txt', 'r').readlines()
				#print log_cluster
				time.sleep(1)
			

	os.chdir('../')

command = 'qstat -u '+uname+'  > log_cluster.txt'
os.system(command)
log_cluster = open('log_cluster.txt', 'r').readlines()
#print log_cluster
while len(log_cluster) != 0:
	command = 'qstat -u '+uname+'  > log_cluster.txt'
	os.system(command)
	log_cluster = open('log_cluster.txt', 'r').readlines()
	#print log_cluster
	time.sleep(1)

for file in files:
	if not os.path.isdir(file) or file[:2] <> 'PA' or len(file) > 6:
		continue
	pacode = file
	print pacode
	os.chdir(file)
	xfiles = os.listdir('./')
	for xfile in xfiles:
		if not os.path.isdir(xfile) or len(xfile.split('_')) <> 3:
			continue
		else:
			print xfile
			xpacode,pdbcode,ligand = xfile.split('_')
			tot_pdbs += 1
			os.chdir(xfile)
			command = '/homes/asarkar/DrugPred2.1/DockLigands.py ' + db + ' ' + datatable + ' ' + desctable + ' ' + uname + ' ' + password + ' ' + pacode + ' ' + pdbcode + ' ' + ligand
			print command
			os.system(command)
			os.chdir('../')
			
			command = 'qstat -u '+uname+'  > log_cluster.txt'
			os.system(command)
			log_cluster = open('log_cluster.txt', 'r').readlines()
			#print log_cluster
			while len(log_cluster) > 102:
				command = 'qstat -u '+uname+'  > log_cluster.txt'
				os.system(command)
				log_cluster = open('log_cluster.txt', 'r').readlines()
				#print log_cluster
				time.sleep(1)
			

	os.chdir('../')

command = 'qstat -u '+uname+'  > log_cluster.txt'
os.system(command)
log_cluster = open('log_cluster.txt', 'r').readlines()
#print log_cluster
while len(log_cluster) != 0:
	command = 'qstat -u '+uname+'  > log_cluster.txt'
	os.system(command)
	log_cluster = open('log_cluster.txt', 'r').readlines()
	#print log_cluster
	time.sleep(1)

for file in files:
	if not os.path.isdir(file) or file[:2] <> 'PA' or len(file) > 6:
		continue
	pacode = file
	print pacode
	os.chdir(file)
	xfiles = os.listdir('./')
	for xfile in xfiles:
		if not os.path.isdir(xfile) or len(xfile.split('_')) <> 3:
			continue
		else:
			print xfile
			xpacode,pdbcode,ligand = xfile.split('_')
			tot_pdbs += 1
			os.chdir(xfile)
			command = '/homes/asarkar/DrugPred2.1/CreateSuperligand.py ' + uname
			print command
			os.system(command)
			os.chdir('../')
			
			command = 'qstat -u '+uname+'  > log_cluster.txt'
			os.system(command)
			log_cluster = open('log_cluster.txt', 'r').readlines()
			#print log_cluster
			while len(log_cluster) > 102:
				command = 'qstat -u '+uname+'  > log_cluster.txt'
				os.system(command)
				log_cluster = open('log_cluster.txt', 'r').readlines()
				#print log_cluster
				time.sleep(1)
			

	os.chdir('../')


command = 'qstat -u '+uname+'  > log_cluster.txt'
os.system(command)
log_cluster = open('log_cluster.txt', 'r').readlines()
#print log_cluster
while len(log_cluster) != 0:
	command = 'qstat -u '+uname+'  > log_cluster.txt'
	os.system(command)
	log_cluster = open('log_cluster.txt', 'r').readlines()
	#print log_cluster
	time.sleep(1)

for file in files:
	if not os.path.isdir(file) or file[:2] <> 'PA' or len(file) > 6:
		continue
	pacode = file
	print pacode
	os.chdir(file)
	xfiles = os.listdir('./')
	for xfile in xfiles:
		if not os.path.isdir(xfile) or len(xfile.split('_')) <> 3:
			continue
		else:
			print xfile
			xpacode,pdbcode,ligand = xfile.split('_')
			tot_pdbs += 1
			os.chdir(xfile)
			command = '/homes/asarkar/DrugPred2.1/ProcessSuperligand.py ' + db + ' ' + datatable + ' ' + desctable + ' ' + uname + ' ' + password + ' ' + pacode + ' ' + pdbcode + ' ' + ligand
			print command
			os.system(command)
			os.chdir('../')
			
			command = 'qstat -u '+uname+'  > log_cluster.txt'
			os.system(command)
			log_cluster = open('log_cluster.txt', 'r').readlines()
			#print log_cluster
			while len(log_cluster) > 102:
				command = 'qstat -u '+uname+'  > log_cluster.txt'
				os.system(command)
				log_cluster = open('log_cluster.txt', 'r').readlines()
				#print log_cluster
				time.sleep(1)
			

	os.chdir('../')

command = 'qstat -u '+uname+'  > log_cluster.txt'
os.system(command)
log_cluster = open('log_cluster.txt', 'r').readlines()
#print log_cluster
while len(log_cluster) != 0:
	command = 'qstat -u '+uname+'  > log_cluster.txt'
	os.system(command)
	log_cluster = open('log_cluster.txt', 'r').readlines()
	#print log_cluster
	time.sleep(1)

print 'Total no. of PDB files covered: ', tot_pdbs