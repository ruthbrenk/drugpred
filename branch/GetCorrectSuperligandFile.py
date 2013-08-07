#!/usr/bin/python

import os,sys,shutil,math
from openeye.oechem import *

### BEGIN grid structure

class gridpoint:
        def __init__(self,x,y,z):
                self.x = x
                self.y = y
                self.z = z
		self.delete = False
		self.keep = False
		self.closest_prot_atom = 0
	def get_x(self):
		return self.x
	def get_y(self):
		return self.y
	def get_z(self):
		return self.z

class grid:
        def __init__(self,xmin,xmax,ymin,ymax,zmin,zmax):
                spacing = 1.5
                self.num_gridpoints = 0
                self.gridpoints = []
                for xx in range(int(xmin),int(xmax)):
                        for yy in range(int(ymin),int(ymax)):
                                for zz in range(int(zmin),int(zmax)):
                                        tempgridpoint = gridpoint(xx,yy,zz)
                                        self.gridpoints.append(tempgridpoint)
                                        self.num_gridpoints+=1
		print 'Total number of gridpoints created for this superligand: ', self.num_gridpoints

### END grid structure
### Copy protein structure to correct directory

### Structure to read superligand atoms

class superligatom:
	def __init__(self,x,y,z,name,number,residue,resnum,occupancy,bfactor):
		self.x = x
		self.y = y
		self.z = z
		self.name = name
		self.number = number
		self.residue = residue
		self.resnum = resnum
		self.occupancy = occupancy
		self.bfactor = bfactor
		self.keep = False
	def get_coordinates(self):
		return [self.x,self.y,self.z]
	def get_name(self):
		return self.name
	def get_number(self):
		return self.number
	def get_residue(self):
		return self.residue
	def get_resnum(self):
		return self.resnum
	def get_occupancy(self):
		return self.occupancy
	def get_bfactor(self):
		return self.bfactor

class superligand:
	def __init__(self):
		self.atoms = []
	def add_atom(self,x,y,z,name,number,residue,resnum,occupancy,bfactor):
		tempatom = superligatom(x,y,z,name,number,residue,resnum,occupancy,bfactor)
		self.atoms.append(tempatom)
	def GetAtoms(self):
		return self.atoms

def read_pdb_file(ifs):
	suplig = superligand()
	for line in ifs.xreadlines():
		if line[:6] == 'ATOM  ' or line[:6] == 'HETATM':
			atomnum 	= int(line[6:11].strip())
			atomname	= line[11:16].strip()
			altloc		= line[16:17].strip()
			resname		= line[17:20].strip()
			chainid		= line[21:22].strip()
			resnum		= int(line[22:26].strip())
			icode		= line[26:27].strip()
			x		= float(line[30:38].strip())
			y		= float(line[38:46].strip())
			z		= float(line[46:54].strip())
			occupancy	= float(line[54:60].strip())
			bfactor		= float(line[60:66].strip())
			symbol		= line[76:78].strip()
			charge		= line[78:80].strip()
			suplig.add_atom(x,y,z,atomname,atomnum,resname,resnum,occupancy,bfactor)
	return suplig

def superligand_pdb_line(atom):
	line = 'ATOM  ' #line length is now 6
	atomnum = atom.get_number()
	length = len(str(atomnum))
	n = 0
	while n < 5-length:
		line = line + ' '
		n = n + 1
	line = line + str(atomnum) + ' ' # line length is now 12
	name = atom.get_name()
	length = len(name)
	n = 0
	while n < 4-length:
		line = line + ' '
		n = n + 1
	line = line + name # line length is now 16
	line = line + ' ' # this is for the altLoc description, which is always empty for the superligand; line length is now 17
	resname = atom.get_residue()
	length = len(resname)
	n = 0
	while n < 3-length:
		line = line + ' '
		n = n + 1
	line = line + resname + '  ' # line length is now 22; includes the chain identifier, which is always NULL for the superligand
	resnum = atom.get_resnum()
	length = len(str(resnum))
	n = 0
	while n < 4-length:
		line = line + ' '
		n = n + 1
	line = line + str(resnum) + '    ' # line length is now 30; includes NULL value for iCode
	x,y,z = atom.get_coordinates()
	length = len(str(x))
	n = 0
	while n < 8-length:
		line = line + ' '
		n = n + 1
	line = line + str(x) # line length is now 38;
	length = len(str(y))
	n = 0
	while n < 8-length:
		line = line + ' '
		n = n + 1
	line = line + str(y) # line length is now 46;
	length = len(str(z))
	n = 0
	while n < 8-length:
		line = line + ' '
		n = n + 1
	line = line + str(z) # line length is now 54;
	occupancy = atom.get_occupancy()
	length = len(str(occupancy))
	n = 0
	while n < 6-length:
		line = line + ' '
		n = n + 1
	line = line + str(occupancy) # line length is now 60;
	bfactor = atom.get_bfactor()
	length = len(str(bfactor))
	n = 0
	while n < 6-length:
		line = line + ' '
		n = n + 1
	line = line + str(bfactor) # line length is now 66
	line = line + '          ' # line length is now 76; this is the empty space required between the z coordinate and element symbol
	line = line + '    \n' #line length is now 80; we do not enter the atom symbol or charge into superligand - not really required
	return line

### Structure to read superligand atoms ends here

curr_dir = sys.argv[1]
protein_file = '../' + sys.argv[2]
ligandname = sys.argv[3]
cofactorname = sys.argv[4]
metalname = sys.argv[5]

os.chdir(curr_dir)

print 'Creating all_corrected.pdb and protein.pdb'

command = 'grep ATOM ./docking/testing/results12/all_corrected.pdb > ./all_corrected.pdb'
os.system(command)
### have to remove all ligand atoms from the protein before working with the protein atoms

#shutil.copyfile(protein_file,'./protein.pdb')
#command = 'grep ATOM ' + protein_file + ' > ./protein.pdb'
#os.system(command)

pfile = open(protein_file,'r')
newpfile = open('./protein.pdb','w')
for iline in pfile.xreadlines():
	if iline[:6] == 'ATOM  ':
		newpfile.write(iline)
	elif iline[:6] == 'HETATM' and iline[17:20].strip() == cofactorname:
		newpfile.write(iline)
	elif iline[:6] == 'HETATM' and iline[17:20].strip() == metalname:
		newpfile.write(iline)
	elif iline[:6] == 'ATOM  ' and iline[17:20].strip() == cofactorname:
		newpfile.write(iline)
	elif iline[:6] == 'ATOM  ' and iline[17:20].strip() == metalname:
		newpfile.write(iline)
pfile.close()
newpfile.close()

### Recognition of H atoms and removal from superligand.
### The SASA determination procedures take too long if H atoms are not removed.

#print 'Removing H atoms from superligand'

supligfile = open('./all_corrected.pdb','r')

numbigsupligatoms = 0

numbigsupligatoms = len(supligfile.readlines())

supligfile.close() # If you do not close the file and reopen it, the 'bigsuperligand.pdb' file will not be written. Code then fails!
supligfile = open('./all_corrected.pdb','r')


if numbigsupligatoms >= 50:
	newsupligfile = open('./bigsuperligand.pdb','w')
	for line in supligfile.xreadlines():
		if line[:6] == 'ATOM  ' or line[:6] == 'HETATM':
#			if line[13] != 'H':
			newsupligfile.write(line)
	newsupligfile.close()
	supligfile.close()
else:
	newsupligfile = open('./superligand.pdb','w')
	for line in supligfile.xreadlines():
		if line[:6] == 'ATOM  ' or line[:6] == 'HETATM':
#			if line[13] != 'H':
			newsupligfile.write(line)
	newsupligfile.close()
	supligfile.close()
	### Create complex.pdb here, for dSASA calculations
	command = 'rm -f ./complex.pdb'
	os.system(command)
	command = 'grep ATOM ./protein.pdb >> complex.pdb'
	os.system(command)
	command = 'grep HETATM ./protein.pdb >> complex.pdb'
	os.system(command)
	command = 'cat superligand.pdb >> complex.pdb'
	os.system(command)
	sys.exit(0) # If the total number of superligand atom is less than 30, keep all the superligand atoms, because it won't delay the SASA calculations


### This procedure still takes wayyyyyyy too long, so I am going to write a new bit of code here
### This code will create a grid box around the superligand and find which grid points
### are close to the protein atoms (within slightly more than the width of a water molecule
### Then, only one atom per remaining gridpoint shall be kept; all others will be deleted
### This should still give us a smaller superligand that covers the surface of the protein

print 'Opening bigsuperligand.pdb and protein.pdb'

ifsx = open('./bigsuperligand.pdb','r')
bigsuperlig = read_pdb_file(ifsx)

ifsy = oemolistream('./protein.pdb')
prot = OEGraphMol()
OEReadMolecule(ifsy,prot)
OEAssignBondiVdWRadii(prot)

# For each atom in bigsuperlig, get min and max x,y,z values
print 'Getting corners for grid'

xarray = []
yarray = []
zarray = []

for atom in bigsuperlig.GetAtoms():
	x,y,z=atom.get_coordinates()
	xarray.append(x)
	yarray.append(y)
	zarray.append(z)

minx = min(xarray)
miny = min(yarray)
minz = min(zarray)
maxx = max(xarray)
maxy = max(yarray)
maxz = max(zarray)

print 'The corners of the grid are: ',minx,maxx,miny,maxy,minz,maxz

# Create a grid using min and max x,y,z values

grid = grid(minx,maxx,miny,maxy,minz,maxz)

# Delete any gridpoints that clash with the protein

print 'Starting identification of gridpoints clashing with protein'

coords = OEFloatArray(prot.GetMaxAtomIdx()*3)
prot.GetCoords(coords)
for point in grid.gridpoints:
	x,y,z = point.x,point.y,point.z
	for atom in prot.GetAtoms():
		idx = atom.GetIdx()
		px,py,pz = coords[idx*3],coords[idx*3+1],coords[idx*3+2]
		d = atom.GetRadius()
		dsquare = math.pow(d,2)
		if dsquare > math.pow(px-x,2) + math.pow(py-y,2) + math.pow(pz-z,2): # compare square of distance, not distance.. is computationally faster
			point.delete = True
			break

remaining_grid_points = []

for point in grid.gridpoints:
	if not point.delete:
		x = point.get_x()
		y = point.get_y()
		z = point.get_z()
		tempgridpoint = gridpoint(x,y,z)
		remaining_grid_points.append(tempgridpoint)

print 'Number of gridpoints kept, not clashing with protein: ', len(remaining_grid_points)

# Delete any gridpoints that are not within 2 Angstroms of at least one protein atom
'''
for point in remaining_grid_points:
	x,y,z = point.x,point.y,point.z
	for atom in prot.GetAtoms():
		idx = atom.GetIdx()
		px,py,pz = coords[idx*3],coords[idx*3+1],coords[idx*3+2]
		if 4 > math.pow(px-x,2) + math.pow(py-y,2) + math.pow(pz-z,2):
			point.keep = True
			break

final_gridpoints = []

for point in remaining_grid_points:
	if point.keep:
		x = point.get_x()
		y = point.get_y()
		z = point.get_z()
		tempgridpoint = gridpoint(x,y,z)
		final_gridpoints.append(tempgridpoint)

print 'Number of grid points kept, close to the protein: ', len(final_gridpoints)
'''
# For remaining gridpoints (which should be few in number), calculate which is the closest bigsuperlig atom

#for gridpoint in final_gridpoints: # This line commented out by AS Nov 15, 2011 and changed to below
for gridpoint in remaining_grid_points:
	x,y,z = gridpoint.x,gridpoint.y,gridpoint.z
	closest_atom_dist_square = 1000000.0
	for atom in bigsuperlig.GetAtoms():
		sx,sy,sz = atom.get_coordinates()
		dsquared = pow(x-sx,2) + pow(y-sy,2) + pow(z-sz,2)
		if closest_atom_dist_square > dsquared:
			idx = bigsuperlig.atoms.index(atom) # Note that the closest atom is now defined by the index of the atom, not the atom number
			gridpoint.closest_prot_atom = idx
			closest_atom_dist_square = dsquared

# Delete all other bigsuperlig atoms

keep_atom_list = []

#for gridpoint in final_gridpoints:
for gridpoint in remaining_grid_points:
	keep_atom_list.append(gridpoint.closest_prot_atom)

keep_atom_set = set(keep_atom_list)

print 'Final atom indices which were kept: ', keep_atom_set

smallsuperlig = superligand()

for atom in bigsuperlig.GetAtoms():
	idx = bigsuperlig.atoms.index(atom)
	if idx in keep_atom_set:
		x,y,z = atom.get_coordinates()
		name = atom.get_name()
		number = atom.get_number()
		residue = atom.get_residue()
		resnum = atom.get_resnum()
		occupancy = atom.get_occupancy()
		bfactor = atom.get_bfactor()
		smallsuperlig.add_atom(x,y,z,name,number,residue,resnum,occupancy,bfactor)

# Write superligand.pdb that contains only the remaining bigsuperlig atoms

ofs = open('./superligand.pdb','w')
for atom in smallsuperlig.GetAtoms():
	linetowrite = superligand_pdb_line(atom)
	ofs.write(linetowrite)

ofs.close()
ifsx.close()

### Create complex.pdb here, for dSASA calculations
command = 'rm -f ./complex.pdb'
os.system(command)
command = 'grep ATOM ./protein.pdb >> complex.pdb'
os.system(command)
command = 'grep HETATM ./protein.pdb >> complex.pdb'
os.system(command)
command = 'cat superligand.pdb >> complex.pdb'
os.system(command)

