#!/usr/bin/env python

#read OUTDOCK file
# keep codes that fullfil score cut-off
#generate pdb file for these molecules
#thin out superligand

import string, os,mysql,math
from openeye.oechem import *

score_cut_off = -1.2
atom_cut_off = 1.2 #C-C distance

#*******************************************************************************


#---------------------------------------------
def gen_mol_list(cut_off):
	mol_list = []
	outdock = open('OUTDOCK', 'r')

	for i in outdock.readlines():
  		if (i[0:6] == '     E') and (string.strip(i[72:79]) <> 'Total'):
    			name = i[7:16]
    			score = float( string.strip( i[71:79] ) )
    			vdw   = float( string.strip( i[37:48] ) )
			if score <> vdw:
				print 'total score <> vdw score <-------------------------------------------'
				print i
				
			else:
				ratio = vdw/nhvy
				if ratio <= cut_off:
					mol_list.append(name)

		else:
			try:
	   			nhvy = float( string.strip( i[39:41] ) ) #nhvy is in line before score
			except:
				continue
	outdock.close()
	return mol_list

#---------------------------------------------
def keep_pdb(mol_list,atom_cut_off):
	atom_list = []
	found = False
	start = False
	poses = open('res.eel1', 'r')
	superlig = open('superligand.pdb', 'w')
	for i in poses.readlines():
		label = i[7:16]
		if i[0:6] == 'REMARK' and label in mol_list:
			label = i[7:16]
			#print label
			start = True
			found = True
		elif start and i.strip() <> 'TER' and i[13] <> 'H': # do not keep hydrogen atoms
			x = float(i[30:38])
			y = float(i[38:46])
			z = float(i[46:54])
			#print i
			#print x,y,z
			if len(atom_list) == 0: #populate list
				atom_list.append([x,y,z])
				found = True  #found at least one molecule that could be docked and meets cut off criteria
			else:
				#print atom_list
				for entry in atom_list: #compare new atom with every atom in atom list
					reject = False
					dsquare = math.pow(atom_cut_off,2)
					#print dsquare, 'here'
					distance = math.pow(entry[0]-x,2) + math.pow(entry[1]-y,2) + math.pow(entry[2]-z,2)
					#print distance, 'distance'
					if distance < dsquare: # compare square of distance, not distance.. Auri claims that this is computationally faster	
						#atom is close to an existing atom -> reject
						reject = True
						#print 'reject atom'
						break #no need to compare the atom any further
				if not reject:
					atom_list.append([x,y,z])
					superlig.write(i)
		elif i.strip() == 'TER':
			start = False

	poses.close()
	superlig.close()

	if not found:
		print 'No atoms in superligand for this PDB Assuming pocket was too tight for docking Substituting superligand with original ligand'
		command = 'cp ../xtal-lig.pdb superligand.pdb'
		os.system(command)

	#AK and AS run correctPDB.py after superligand, not sure why this is needed


#---------------------------------------------

#MAIN

mol_list = gen_mol_list(score_cut_off)
keep_pdb(mol_list, atom_cut_off)







		
 

