#!/usr/bin/python

import os, sys
from openeye.oechem import *
from openeye.oespicoli import *
import mysql
import MySQLdb

### Declare list of hydrophobic residues and hydrophobicity index dictionary

hydrophobic_reslist = ['ALA', 'GLY', 'VAL', 'ILE', 'LEU', 'MET', 'PHE', 'PRO']
hydrophobicity_indices = {'ALA':1.8, 'ARG':-4.5, 'ASN':-3.5, 'ASP':-3.5, 'CYS':2.5, 'GLN':-3.5, 'GLU':-3.5, 'GLY':-0.4, 'HIS':-3.2, 'ILE':4.5, 'LEU':3.8, 'LYS':-3.9, 'MET':1.9, 'PHE':2.8, 'PRO': -1.6, 'SER':-0.8, 'THR':-0.7, 'TRP':-0.9, 'TYR':-1.3, 'VAL':4.2}
aa_residues = ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL']

### Declare values for grid spacing and probe radius during surface area calculations

proberad = 1.0
gridspacing = 0.5

### Change over to correct directory

curr_dir = sys.argv[3]
os.chdir(curr_dir)

#### Call in protein
iprotfs = oemolistream(sys.argv[1])
prot = OEGraphMol()

if not OEReadMolecule(iprotfs,prot):
	print "Protein file unreadable"
	sys.exit(0)

#### Call in protein-superligand complex
icplxfs = oemolistream(sys.argv[2])
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

### Calculate any SASA changes for every atom in protein when converted to complex

backbone_atoms = ['N','CA','C','O']
num_apolar_res = 0.0 # Float required, because otherwise division removes decimal points
num_res = 0
hydrophobic_sasa_total = 0.0
hydrophilic_sasa_total = 0.0
sasa_total = 0.0
sum_hydrophobicity_index = 0.0

all_res = []
haa_covered_res = []
hiaa_covered_res = []

for atom in prot.GetAtoms():
	idx = atom.GetIdx()
	name = atom.GetName()
	resname = OEAtomGetResidue(atom).GetName()
	resnum = OEAtomGetResidue(atom).GetResidueNumber()
	for iatom in cplx.GetAtoms():
		iidx = iatom.GetIdx()
		iname = iatom.GetName()
		iresname = OEAtomGetResidue(iatom).GetName()
		iresnum = OEAtomGetResidue(iatom).GetResidueNumber()
		if idx == iidx and name == iname and resname == iresname and resnum == iresnum:
			deltasasa = atomareas[atom.GetIdx()] - iatomareas[iatom.GetIdx()]
			if deltasasa <> 0.0:
				#print idx, name, resname, resnum, deltasasa
				sasa_total = sasa_total + deltasasa
				if atom.GetAtomicNum() <= 6: # If it is not a Carbon or a Hydrogen, assume it to be polar.
					hydrophobic_sasa_total = hydrophobic_sasa_total + deltasasa
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
			break

# CALCULATIONS FOR THE ENCLOSURE DESCRIPTOR
# Calculate SASA change for superligand

isupligfs = oemolistream(sys.argv[9])
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
print 'csa: ', csa, 'hsa_t: ', hsa_t, 'psa_r: ', psa_r, 'hiaa: ', hiaa, 'haa: ', haa
print 'fsasa: ', fraction_sasa_change, 'dsasa: ', not_buried_sasa
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

db = str(sys.argv[4]) # Database
tb = str(sys.argv[5]) # Table
dt = str(sys.argv[6]) # Descriptor Table
us = str(sys.argv[7]) # Username
pw = str(sys.argv[8]) # Password
wantedpacode = str(sys.argv[10]) # PA code for Pseudomonas protein
wantedpdb = str(sys.argv[11]) # 4 letter code for PDB
wantedlig = str(sys.argv[12]) # 3 letter code for ligand bound to protein

conn=mysql.connect2server(pw, us, db)
cursor = conn.cursor ()

command = "Select * from "+ dt +" where id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
cursor.execute(command)

label_exists = cursor.fetchall()

if len(label_exists) > 0:
	command = "UPDATE " + dt + " SET csa = " + str(csa) + " WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)
	
	command = "UPDATE " + dt + " SET hsa_t = " + str(hsa_t) + " WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)
	
	command = "UPDATE " + dt + " SET psa_r = " + str(psa_r) + " WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)
	
	command = "UPDATE " + dt + " SET hiaa = " + str(hiaa) + " WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)
	
	command = "UPDATE " + dt + " SET haa = " + str(haa) + " WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)
	
	command = "UPDATE " + dt + " SET dsasa = " + str(not_buried_sasa) + " WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)

	command = "UPDATE " + dt + " SET fsasa = '" + str(fraction_sasa_change) + "' WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)

	command = "UPDATE " + dt + " SET prediction = '" + prediction + "' WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)

	command = "UPDATE " + dt + " SET prediction = '" + prediction + "' WHERE id = '" + wantedpdb +"' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "'"
	cursor.execute(command)
else:
	command = "INSERT INTO " + dt + "  (pacode,id,lig,csa,hsa_t,psa_r,hiaa,haa,dsasa,fsasa,score,prediction) values ( '" + wantedpacode + "','" + wantedpdb + "','" + wantedlig + "'," + str(csa) + "," + str(hsa_t) + "," + str(psa_r)  + "," + str(hiaa) + "," + str(haa) + "," + str(not_buried_sasa) + "," + str(fraction_sasa_change) + "," + str(score) + ",'" + prediction + "')"
	cursor.execute(command)
cursor.close ()
conn.commit()
conn.close ()
