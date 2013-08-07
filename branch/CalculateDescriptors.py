#!/usr/bin/python

import os,sys,shutil, time
import mysql
import MySQLdb

curr_dir = sys.argv[1]
db = str(sys.argv[2]) # Database
tb = str(sys.argv[3]) # Table
dt = str(sys.argv[4]) # Descriptor table
uname = str(sys.argv[5]) # Username
pword = sys.argv[6] # Password
pacode = sys.argv[7]
wantedpdb = sys.argv[8]
wantedlig = sys.argv[9]


os.chdir(curr_dir)

files = os.listdir('./')
files.sort()
path = os.path.abspath(os.path.curdir)
for file_ in files:
        if file_[-4:] == '.pdb':
		os.chdir(path)
		pdb_code = file_[:-4]
		os.chdir(pdb_code)	# cd in new directory and do docking stuff
		newpath = os.path.abspath(os.path.curdir)
		
		# Connect to the MySQL database
		
		conn=mysql.connect2server(pword, uname, db)
		cursor = conn.cursor ()
		
		# Get the name of the cofactor
		
		command = "select lig, cof, metal from "+tb+" where id = '" + wantedpdb +"' and pacode = '" + pacode + "' and lig = '" + wantedlig + "' limit 1"
		cursor.execute(command)
		rows = cursor.fetchall ()
		
		conn.close()
		cursor.close()
		
		ligand = rows[0][0]
		cofactor = str(rows[0][1])
		metal = str(rows[0][2])
		
		if cofactor == '':
			cofactor = '-'
		if metal == '':
			metal = '-'
		
		
		# Now, get correct superligand, that has only protein, cofactor and metal.
		
		#command = 'qsub -cwd /homes/asarkar/DrugPred2.1/GetCorrectSuperligandFile.py ' + newpath + ' ' + file_ + ' ' + ligand + ' ' + cofactor + ' ' + metal
		command = '/homes/asarkar/DrugPred2.1/GetCorrectSuperligandFile.py ' + newpath + ' ' + file_ + ' ' + ligand + ' ' + cofactor + ' ' + metal
		os.system(command)
		
		os.chdir(path)
		pdb_code = file_[:-4]
		os.chdir(pdb_code)	# cd in new directory and do docking stuff
		command = '/homes/asarkar/DrugPred2.1/CalculateAtomicAccessibility.py protein.pdb complex.pdb ' + os.path.abspath(os.path.curdir) + ' ' + db + ' ' + tb + ' ' + dt + ' ' + uname + ' ' + pword + ' ' + 'superligand.pdb ' + pacode + ' ' + wantedpdb + ' ' + wantedlig
		os.system(command)

