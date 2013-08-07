#!/usr/bin/python
#split dock output into single pdb-files and store additonal information in seperate files, only convert the highest scoring molecule per label

import sys, string, os

from openeye.oechem import *
#import openeye 

if len(sys.argv) <> 2:
	print 'dock2mol2_high_scoring.py ../*.eel1'
	sys.exit()


#Name of output file
output = open('label_scores.txt', 'w')
end_of_molecule = 'true'

#output_file = open(output, 'r')
print 'hier'
data_list = []
general_list = []
unique_list = []
count_dic = {}

file = sys.argv[1]

dict = {}
#-------------------------------
def format_pdb(file):

   in_file = open(file, 'r')
   
   pdb_file = open(file[:-5] + '.pdb', 'w')
   for i in in_file.xreadlines():
     if i[:6] == 'REMARK':
       if i[17:23] == 'energy':
         #in case of flex receptor :> line is to long
	 if len(i)  > 72:
	   new_line = i[:69] + string.strip(i[72:])
	 else:
	   new_line = 1
         pdb_file.write(new_line + '\n')
     elif i[:4] == 'ATOM':
       pdb_file.write(i[:56] + '    ' + i[56:])	
     else:
       pdb_file.write(i) 
       
   pdb_file.close()
   in_file.close()
     
#-------------------------------
def mol2(mol):
   
  outfile = mol.GetTitle() + '.mol2'
  ofs = oemolostream(outfile)
  #mol = OEGraphMol()
  
  #if OEReadPDBFile => tripos atom types don"t match
  #if OEReadMolecule => it assigns implicit hydrogens, which can be a problem with Chinones
  
  
  
  for atom in mol.GetAtoms():
     res =  OEAtomGetResidue(atom)
     atom.SetPartialCharge(res.GetBFactor())
     #print atom.GetPartialCharge()
     #there are no implict hydrogens
     atom.SetImplicitHCount(0)

     
    
  OEDetermineConnectivity(mol)
  OEPerceiveBondOrders(mol)
  OEFindRingAtomsAndBonds(mol)
  OETriposAtomTypes(mol)
  OETriposAtomTypeNames(mol)
  OETriposBondTypeNames(mol)
  OETriposAtomNames(mol)
  OEAssignAromaticFlags(mol)

  
  OEWriteMolecule(ofs,mol)
  ofs.close()

#-------------------------------
  

print "reformating file"
format_pdb(file)

ifs = oemolistream()
ifs.open(file[:-5] + '.pdb')
mol = OEGraphMol()
  
  
print "spliting file"

ifs.SetFlavor(OEFormat_PDB,OEIFlavor_PDB_DEFAULT|OEIFlavor_PDB_DATA|OEIFlavor_PDB_TER)

while OEReadMolecule(ifs, mol):
  for pdbdata in OEGetPDBDataPairs(mol):
    #print "PDBTag:",pdbdata.GetTag()
    line = OEGetPDBData(mol,pdbdata.GetTag())
    
    label = string.strip(line[0:11]) 
    score = string.strip(line[19:30])
    
    #print score
    try:
       test = float(score)
    except:
       score = '9999999999999'
    #if score == '*********' :
    #  score = '99999999999999999'
    receptor = string.strip(line[60:])
    
    mol.SetTitle(label)
    if not dict.has_key(label):
       dict[label]  = [score,receptor]
       mol2(mol)
    elif float(dict[label][0]) > float(score):
       dict[label] = [score,receptor]
       mol2(mol)
       
list = []
list = dict.items()
list.sort()
for i in list:
#  print i
  output.write(i[0] + '\t' + i[1][0] + '\t' + i[1][1] + '\n')
  
output.close()
        
 
  

