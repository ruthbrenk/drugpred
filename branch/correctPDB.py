#!/usr/bin/python

import sys, string,os

#from openeye.oechem import *
#from openeye.oeshape import *

in_file = open(sys.argv[1], 'r')
out_file = open(sys.argv[2], 'w')
#corrected_file_name = in_file[:-4] + '_corr.pdb' 
#corrected_file = open(corrected_file_name, 'w')
counter = 0
res_counter = 188


for line in  in_file.readlines():
	if line[0:4] == 'ATOM' :
		line1 = line
		counter = counter + 1
		new_line = line[:22] + string.rjust(str(res_counter), 4) + line[26:] #3 zu 4 geaendert
		out_file.write(new_line)
	elif line[0:6] == 'CONECT':
		out_file.write(line)
	elif line == 'END\n':
		counter = counter + 1
		new_line2 = 'TER   ' + '           ' +line1[17:22] + string.rjust(str(res_counter), 4) + line[26:]+'\n'
#TER    2903      PHE A 382

		out_file.write(new_line2)
		res_counter = res_counter + 1
out_file.write('END')
out_file.close()

#ifs = oemolistream(corrected_file_name)
#mol = OEGraphMol()
#OEReadPDBFile(ifs,mol)
#vol = OECalcVolume(mol, False)
#print vol
#print file[36:40]
#identifier = str(pdb_code[36:40])
#str(file).split('/', 1)

#out_file.write(identifier + '\t' + str(vol) + '\n' )

in_file.close()
#out_file.close()
