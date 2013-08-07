#!/usr/bin/python

import os, sys, string

#'scritp to get mol2 files which fulfil cutoff in one folder'

input_file = open(sys.argv[1], 'r')

print sys.argv[1]

for i in input_file.readlines():
	#print i
	mol_name, bla1, bla2, bla = string.split(i.strip(),'\t')
	#mol_name = line[0]
	print mol_name
	command = 'cp ../acd.mdb/'+mol_name+'.mol2 .'
	print command
	os.system(command)

	command = '/software/babel/babel -imol2 '+mol_name+'.mol2 -opdb ' +mol_name+'.pdb -e'
	os.system(command)
	
	command = 'rm -f ' + mol_name + '.mol2'
	os.system(command)
	
	command = 'cat ' + mol_name + '.pdb >> all.pdb'
	os.system(command)
	
	command = 'rm -f ' + mol_name + '.pdb'
	os.system(command)

command = 'rm -Rf ../acd.mdb'
os.system(command)

if not os.path.exists('all.pdb'):
	ofile = open('zeroatoms','w')
	ofile.write('No atoms in superligand for this PDB\nAssuming pocket was too tight for docking\nSubstituting superligand with original ligand')
	ofile.close()
	command = 'cp ../../xtal-lig.pdb ./all.pdb'
	os.system(command)

command = 'python /homes/asarkar/DrugPred2.1/correctPDB.py all.pdb all_corrected.pdb'
os.system(command)

print '------------------------------------------------------------------'
