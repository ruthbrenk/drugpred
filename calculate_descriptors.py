#!/usr/bin/env python

import os, sys
from openeye.oechem import *
from openeye.oespicoli import *
import mysql
import MySQLdb


#spicoli is buggy, if CL,BR,or I present in superligand (F seems to be fine) surface of atoms of superligand complex outside binding site changes!!!!
#TO DO: set all superligand atoms to C
#introduce check, that radius of first atom in prot file and sl complex is the same
#added code to calculate aromatic SA and charged SA


#*******************************************************************************
# MAIN help
#**********

outhelp = 0
if len(sys.argv) == 2 and sys.argv[1] == "--help":
	outhelp = 1
elif len(sys.argv) != 13:
	outhelp = 1
elif sys.argv[1] != "-db" or sys.argv[3] != "-tb" or sys.argv[5]  != "-user"  or sys.argv[7] != "-password" or sys.argv[9] != "-id" or sys.argv[11] != "-dt":
	outhelp = 1


if outhelp == 1:
	print "*** Script to calculate descriptos ***\n"
	print "Written by Agata Krasowski, Auri and RB\n"
	print "Usage:   --help shows this help"
	print "         -db [data base] -tb [data table] -user [username db] -password [password] -id [id] -dt [descriptor table]"

	sys.exit()


### Declare list of hydrophobic residues and hydrophobicity index dictionary

hydrophobic_reslist = ['ALA', 'GLY', 'VAL', 'ILE', 'LEU', 'MET', 'PHE', 'PRO']
hydrophobicity_indices = {'ALA':1.8, 'ARG':-4.5, 'ASN':-3.5, 'ASP':-3.5, 'CYS':2.5, 'GLN':-3.5, 'GLU':-3.5, 'GLY':-0.4, 'HIS':-3.2, 'ILE':4.5, 'LEU':3.8, 'LYS':-3.9, 'MET':1.9, 'PHE':2.8, 'PRO': -1.6, 'SER':-0.8, 'THR':-0.7, 'TRP':-0.9, 'TYR':-1.3, 'VAL':4.2}
aa_residues = ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL']

charged_atoms = ['OE1', 'OE2', 'NZ','OD1', 'OD2','NE','NH1','NH2','ZN','MG','CA','MN','FE','NI'] 

### Declare values for grid spacing and probe radius during surface area calculations

proberad = 1.0
gridspacing = 0.5

#get values from db
db = str(sys.argv[2])
tb = str(sys.argv[4])
us = str(sys.argv[6])
pw = str(sys.argv[8])
id = str(sys.argv[10])
dt = str(sys.argv[12])

conn=mysql.connect2server(pw, us, db)  			    
cursor = conn.cursor ()

command = "select prot, lig, cof, metal from " + tb + " where id = '" + id + "'"
print command
cursor.execute(command)
rows = cursor.fetchall ()

prot = rows[0][0]

prot_cofac = prot + '_cofac.pdb'
print prot_cofac


#### Call in protein
iprotfs = oemolistream(prot_cofac)
prot = OEGraphMol()

if not OEReadMolecule(iprotfs,prot):
	print "Protein file unreadable"
	sys.exit(0)



#### Call in protein-superligand complex
command = 'cat ' + prot_cofac + ' ./testing/superligand.pdb > sl_' + prot_cofac
os.system(command)
icplxfs = oemolistream('sl_' + prot_cofac)
cplx = OEGraphMol()

if not OEReadMolecule(icplxfs,cplx):
	print "Complex file unreadable"
	sys.exit(0)


#### Print atomic accessibility for each of these

# PROTEIN
OEAssignBondiVdWRadii(prot)

surf = OESurface()

if not OEMakeAccessibleSurface(surf,prot,proberad,gridspacing):
#if not OEMakeMolecularSurface(surf,prot,proberad,gridspacing):
	print "Could not create accessible surface for molecule"
	sys.exit(0)

areas = OEFloatArray(surf.GetNumTriangles())
OECalculateTriangleAreas(surf,areas)

atomareas = [0.0]*prot.GetMaxAtomIdx()

for i in range(surf.GetNumTriangles()):
	v1 = surf.GetTrianglesElement(i*3)
	v2 = surf.GetTrianglesElement(i*3+1)
	v3 = surf.GetTrianglesElement(i*3+2)
	
	a1 = surf.GetAtomsElement(v1)
	a2 = surf.GetAtomsElement(v2)
	a3 = surf.GetAtomsElement(v3)
	
	atomareas[a1] += areas[i]/3.0
	atomareas[a2] += areas[i]/3.0
	atomareas[a3] += areas[i]/3.0




# PROTEIN-SUPERLIGAND COMPLEX
OEAssignBondiVdWRadii(cplx)

isurf = OESurface()

if not OEMakeAccessibleSurface(isurf,cplx,proberad,gridspacing):
#if not OEMakeMolecularSurface(surf,cplx,proberad,gridspacing):
	print "Could not create accessible surface for molecule"
	sys.exit(0)

iareas = OEFloatArray(isurf.GetNumTriangles())
OECalculateTriangleAreas(isurf,iareas)

iatomareas = [0.0]*cplx.GetMaxAtomIdx()

for i in range(isurf.GetNumTriangles()):
	v1 = isurf.GetTrianglesElement(i*3)
	v2 = isurf.GetTrianglesElement(i*3+1)
	v3 = isurf.GetTrianglesElement(i*3+2)
	
	a1 = isurf.GetAtomsElement(v1)
	a2 = isurf.GetAtomsElement(v2)
	a3 = isurf.GetAtomsElement(v3)
	
	iatomareas[a1] += iareas[i]/3.0
	iatomareas[a2] += iareas[i]/3.0
	iatomareas[a3] += iareas[i]/3.0

#check that diff of atoms outside binding site is 0, there is a bug in Spicoli

for atom in prot.GetAtoms():
	free_atom_area = atomareas[atom.GetIdx()]
	#print "atom", atom.GetIdx(), "area = %2.4f" % free_atom_area
	
	cplx_atom = cplx.GetAtom(OEHasAtomIdx(atom.GetIdx()))
	cplx_atom_area =  iatomareas[cplx_atom.GetIdx()]
	#print "atom cplx", cplx_atom.GetIdx(), "area = %2.4f" % cplx_atom_area
	if free_atom_area - cplx_atom_area <> 0:
		print "Warning: Surface area of first atom in protein changes upon complex formation. If this atom is not part of the binding site, this is a bug."
	break #one check is enough
	



### Calculate any SASA changes for every atom in protein when converted to complex

backbone_atoms = ['N','CA','C','O']
num_apolar_res = 0.0 # Float required, because otherwise division removes decimal points
num_res = 0
hydrophobic_sasa_total = 0.0
hydrophilic_sasa_total = 0.0
sasa_total = 0.0
aromatic_sasa_total = 0.0
charged_sasa_total = 0.0
sum_hydrophobicity_index = 0.0

all_res = []
haa_covered_res = []
hiaa_covered_res = []

mol = OEGraphMol()


for atom in prot.GetAtoms():
	idx = atom.GetIdx()
	name = atom.GetName()
	resname = OEAtomGetResidue(atom).GetName()
	resnum = OEAtomGetResidue(atom).GetResidueNumber()
	#get same atom from complex
	#print idx
	iatom = cplx.GetAtom(OEHasAtomIdx(idx))

	iidx = iatom.GetIdx()
	iname = iatom.GetName()
	iresname = OEAtomGetResidue(iatom).GetName()
	iresnum = OEAtomGetResidue(iatom).GetResidueNumber()
	if idx == iidx and name == iname and resname == iresname and resnum == iresnum: #that's code from Auri, I guess he did not trust that the atom was really the same
			deltasasa = atomareas[atom.GetIdx()] - iatomareas[iatom.GetIdx()]
			if deltasasa <> 0.0:
				#print idx, name, resname, resnum, deltasasa
				mol.NewAtom(atom) #save atom to generate binding site 
				#print atom.GetName(), atom.GetAtomicNum()
				sasa_total = sasa_total + deltasasa
				if atom.GetAtomicNum() <= 6: # If it is not a Carbon or a Hydrogen, assume it to be polar.
					hydrophobic_sasa_total = hydrophobic_sasa_total + deltasasa
				if atom.IsAromatic():
					aromatic_sasa_total = aromatic_sasa_total  + deltasasa
					#print 'aromatic', atom.GetName()
				elif atom.GetName().strip() in charged_atoms and atom.GetAtomicNum() <>6 : #CA only for metal, not Carbon 
					charged_sasa_total = charged_sasa_total + deltasasa
					#print 'charged', atom.GetName()
				resid = resname.strip()+str(resnum).strip()
				if resid not in all_res:
					all_res.append(resid)
					num_res += 1
				if resname in hydrophobic_reslist and name.strip() not in backbone_atoms:
					if resid not in haa_covered_res:
						num_apolar_res += 1
						haa_covered_res.append(resid)
				if resname in aa_residues and name.strip() not in backbone_atoms: # Do not try to find hiaa for backbone atoms, cofactors & metals
					if resid not in hiaa_covered_res:
						sum_hydrophobicity_index = sum_hydrophobicity_index + hydrophobicity_indices[resname]
						hiaa_covered_res.append(resid)
	else:
		print 'something strange happened, atoms do not match'

ofs = oemolostream() #save binding site 
ofs.open('poc.pdb')
OEWriteMolecule(ofs, mol)
ofs.close()


# CALCULATIONS FOR THE ENCLOSURE DESCRIPTOR
# Calculate SASA change for superligand

isupligfs = oemolistream('testing/superligand.pdb')
suplig = OEGraphMol()
OEReadMolecule(isupligfs,suplig)

OEAssignBondiVdWRadii(suplig)

iisurf = OESurface()

if not OEMakeAccessibleSurface(iisurf,suplig,proberad,gridspacing):
#if not OEMakeMolecularSurface(surf,cplx,proberad,gridspacing):
	print "Could not create accessible surface for superligand"
	sys.exit(0)

iiareas = OEFloatArray(iisurf.GetNumTriangles())
OECalculateTriangleAreas(iisurf,iiareas)

iiatomareas = [0.0]*suplig.GetMaxAtomIdx()

for i in range(iisurf.GetNumTriangles()):
	v1 = iisurf.GetTrianglesElement(i*3)
	v2 = iisurf.GetTrianglesElement(i*3+1)
	v3 = iisurf.GetTrianglesElement(i*3+2)
	
	a1 = iisurf.GetAtomsElement(v1)
	a2 = iisurf.GetAtomsElement(v2)
	a3 = iisurf.GetAtomsElement(v3)
	
	iiatomareas[a1] += iiareas[i]/3.0
	iiatomareas[a2] += iiareas[i]/3.0
	iiatomareas[a3] += iiareas[i]/3.0

superligand_delta_sasa_total = 0.0 # This variable will give the total change in SASA of superligand when it is in complex with protein.
superligand_sasa_total = 0.0 # This variable will contain the total SASA of the superligand when not complexed with protein

for supligatom in suplig.GetAtoms():
	idx = supligatom.GetIdx()
	name = supligatom.GetName()
	resname = OEAtomGetResidue(supligatom).GetName()
	resnum = OEAtomGetResidue(supligatom).GetResidueNumber()
	for atom in cplx.GetAtoms():
		iidx = atom.GetIdx()
		iname = atom.GetName()
		iresname = OEAtomGetResidue(atom).GetName()
		iresnum = OEAtomGetResidue(atom).GetResidueNumber()
		#print idx, iidx, name, iname, resname, iresname, resnum, iresnum
		if name == iname and resname == iresname and resnum == iresnum: # Idx matching requirement removed because Indices need not be the same
			superligand_sasa_total += iiatomareas[idx]
			deltasasa = iiatomareas[idx] - iatomareas[iidx]
			superligand_delta_sasa_total += deltasasa
			#print deltasasa, superligand_delta_sasa_total, superligand_sasa_total
			break

# Calculate final descriptors

fraction_sasa_change = superligand_delta_sasa_total/superligand_sasa_total
# the fraction_sasa_change might not correlate with druggability, because it will be the same for a druggable and a nondruggable site of similar shapes
# but proportionally different sizes. Perhaps we could consider the total surface area of superligand buried inside the pocket instead? Done below!
not_buried_sasa = superligand_sasa_total - superligand_delta_sasa_total


csa = sasa_total
hsa_t = hydrophobic_sasa_total
hydrophilic_sasa_total = sasa_total-hsa_t
psa_r = hydrophilic_sasa_total/sasa_total
hiaa = sum_hydrophobicity_index/float(num_res)
haa = num_apolar_res/float(num_res)

asa = aromatic_sasa_total
chsa = charged_sasa_total 
asa_r = asa/csa
chsa_r = chsa/csa
print 'csa: ', csa, 'hsa_t: ', hsa_t, 'psa_r: ', psa_r, 'hiaa: ', hiaa, 'haa: ', haa
print 'fsasa: ', fraction_sasa_change, 'dsasa: ', not_buried_sasa
print 'asa: ', asa, 'asa_r: ', asa_r, 'chsa: ', chsa, 'chsa_r: ', chsa_r
print -0.2*(psa_r/0.66), 0.16*(hsa_t/995.5), 0.11*(csa/1564.24), 0.22*(haa/0.67), 0.22*(hiaa/1.29), 1.3
# Calculate score
# The descriptors HAVE NOW BEEN NORMALIZED TO UNIT VARIANCE.
# However, they score obtained is still turning out to be too high. I cannot understand why that is
# Will investigate this later on.

score = -0.2*(psa_r/0.66) + 0.16*(hsa_t/995.5) + 0.11*(csa/1564.24) + 0.22*(haa/0.67) + 0.22*(hiaa/1.29) + 1.3
print score
if score <= 0.50:
	prediction = 'less_druggable'
elif score > 0.59:
	prediction = 'druggable'


# Upload descriptors into new format table

command = "Select * from "+ dt +" where id = '" + id  +"'"
print command
cursor.execute(command)

label_exists = cursor.fetchall()

if len(label_exists) > 0:
	command = "delete from " + dt + " WHERE id = '" + id + "'"
	print command
	cursor.execute(command)

command = "INSERT INTO " + dt + "  (id,csa,hsa_t,psa_r,hiaa,haa,dsasa,fsasa,score,prediction,asa,asa_r,chsa,chsa_r) values ( '" + id  + "',"  + str(csa) + "," + str(hsa_t) + "," + str(psa_r)  + "," + str(hiaa) + "," + str(haa) + "," + str(not_buried_sasa) + "," + str(fraction_sasa_change) + "," + str(score) + ",'" + prediction + "'" + ","  + str(asa) + ","  + str(asa_r) + ","  + str(chsa) + ","  + str(chsa_r) + ")"
print command
cursor.execute(command)
cursor.close ()
conn.commit()
conn.close ()
