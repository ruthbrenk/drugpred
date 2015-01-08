#!/usr/bin/env python
# should convert pdb file to format required for docking, prepares also co-factor files
#formerly known as setPDBatomsC.py
#I think we need Protein plus co-factor + metal, ligand file (AK had more, keep an eye on these changes)
#introduced check that ligand occurs only once in PDB file (RB)

import os,sys,string, os.path
import string,os, sys, mysql
import MySQLdb
from openeye.oechem import *




#*******************************************************************************
# MAIN help
#**********

outhelp = 0
if len(sys.argv) == 2 and sys.argv[1] == "--help":
	outhelp = 1
elif len(sys.argv) != 13:
	outhelp = 1
elif sys.argv[1] != "-db" or sys.argv[3] != "-tb" or sys.argv[5]  != "-dt" or sys.argv[7]  != "-user"  or sys.argv[9] != "-password" or sys.argv[11] != "-id":
	outhelp = 1


if outhelp == 1:
	print "*** Script to set protein atoms to C and write in new file, adds cofactor to new file, writes ligand into xtal-lig.pdb, connects to the db to get ligand and cofactor information ***\n"
	print "Written by Agata Krasowski *a.krasowski@dundee.ac.uk*\n"
	print "Usage:   --help shows this help"
	print "         -db [data base] -tb [data table] -user [username db] -password [password] -id [id]"

	sys.exit()

#*******************************************************************************
# MAIN
#***************

docking_scripts = os.environ['DockingScripts']
drugpred_scripts = os.environ['DrugPred']

db = str(sys.argv[2])
tb = str(sys.argv[4])
dt = str(sys.argv[6])
us = str(sys.argv[8])
pw = str(sys.argv[10])
id = str(sys.argv[12])

conn=mysql.connect2server(pw, us, db)  			    
cursor = conn.cursor ()

command = "select prot, lig, cof, metal from " + tb + " where id = '" + id + "'"
print command
cursor.execute(command)
rows = cursor.fetchall ()

prot = rows[0][0]
print prot
input_file_name = prot + '.pdb'
#check if file exits
if not os.path.isfile(input_file_name):
	#file does not exist
	print 'file ', input_file_name, ' does not exist' 
	command = 'insert into ' + dt + ' (id, comment) values ( "' + id + '", "' + input_file_name + ' does not exist")'
	#print command
	cursor.execute(command)
	conn.commit()
	sys.exit()
pdb_file = open(prot + '.pdb', 'r') #input file
out_file_protein= open(prot + '_C.pdb','w') #output file
out_file_protein_cofact= open(prot + '_cofac.pdb','w') #output file


ligand = rows[0][1]
print ligand
out_file_ligand= open(prot + '_' + ligand + '_lig.pdb','w')

cofactor = str(rows[0][2])
print cofactor

metal = str(rows[0][3])
print metal

#make sure that ligand appears only once in file
ifs = oemolistream(prot + '.pdb')
mol = OEGraphMol()
while OEReadMolecule(ifs, mol):
	res_prop = []
	for atom in mol.GetAtoms():
		thisRes = OEAtomGetResidue(atom)
		res_name = thisRes.GetName()
		if res_name == ligand:
			#print res_name, thisRes.GetResidueNumber(), thisRes.GetChainID()
			res_number = thisRes.GetResidueNumber()
			res_chain = thisRes.GetChainID()
			if len(res_prop) == 0:
				#store information on chain and residue number
				res_prop = [res_number, res_chain]
			else:
				#check if different chain and / or residue number
				if res_number <> res_prop[0] or res_chain <> res_prop[1]:
					#duplicate ligand entry
					print 'WARNING!!!!!!!'
					print 'Ligand', ligand, 'occurs twice in file'

ifs.close()
#check finished


#HETATM 4666 ZN    ZN A 701      43.821  38.240  46.712  1.00 25.11          ZN  
#HETATM 4667  O1  LPR A 702      40.291  33.743  45.120  1.00 13.04           O  
for i in pdb_file.readlines():
	i  = i[:20]+'   '+i[23:] #replace chain letter

	if i[:4]=="ATOM": #These lines contain the relevant information
		out_file_protein_cofact.write(i)
		outline="ATOM   "+i[7:11]+" "+ " CX" +"  "+"AAA"+""+i[20:54]+" \n"
		out_file_protein.write(outline)

	if i[:6]=="HETATM": #If structure contains cofactor, write it in pdb_output file
		if i[17:20] == cofactor:
			i = string.replace(i, 'HETATM', 'ATOM  ') #just to be save
			out_file_protein_cofact.write(i)
			outline="ATOM   "+i[7:11]+" "+ " CX" +"  "+"AAA"+""+i[20:54]+" \n"
 			out_file_protein.write(outline)
		elif i[17:20] == ligand:
			outline = string.replace(i, 'HETATM', 'ATOM  ') #HETATM must be ATOM in xtal-lig.pdb
			#print outline
			#print outline
			out_file_ligand.write(outline)
		elif i[17:20] == ' '+metal:
			i = string.replace(i, 'HETATM', 'ATOM  ') #just to be save
			out_file_protein_cofact.write(i)
			outline="ATOM   "+i[7:11]+" "+ " CX" +"  "+"AAA"+""+i[20:54]+" \n"
			out_file_protein.write(outline)


out_file_ligand.close()
out_file_protein.close()
out_file_protein_cofact.close()


command = 'cp ' + prot + '_' + ligand + '_lig.pdb' + ' xtal-lig.pdb'
print command
os.system(command)

#command = 'touch xtal-lig.mol2' 
#os.system(command)

		
#create rec.amb
command = docking_scripts + 'pdb2amb.py ' + prot + '_C.pdb rec.amb'
print command
os.system(command)

#create link from rec.amb to rec.pdb
command = 'ln -s rec.amb rec.pdb'
print command
os.system(command)

#make file
command = 'make auto -f ' + drugpred_scripts + '/Makefile_DrugPred'
print command
os.system(command)

#INDOCK
command = 'cp ' + drugpred_scripts + '/INDOCK testing'
print command
os.system(command)



#do docking
os.chdir('testing')
command = 'ln -s ' + drugpred_scripts + 'db/drug_moles.db .'
os.system(command)

os.system('dock.csh')

os.chdir('../') #back to directory docking

print 'finished docking'

cursor.close()
conn.close()

