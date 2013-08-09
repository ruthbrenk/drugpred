#!/usr/bin/python
# should convert pdb file given by Sybyl to format required for xtal-lig.pdb 
import os,sys,string
import string,os, sys, mysql
import MySQLdb



#*******************************************************************************
# MAIN help
#**********

outhelp = 0
if len(sys.argv) == 2 and sys.argv[1] == "--help":
	outhelp = 1
elif len(sys.argv) != 18:
	outhelp = 1
elif sys.argv[1] != "-fi" or sys.argv[3] != "-fop" or sys.argv[5] != "-fol" or sys.argv[7] != "-db" or sys.argv[9] != "-tb" or sys.argv[11]  != "-user"  or sys.argv[13] != "-password":
	outhelp = 1


if outhelp == 1:
	print "*** Script to set protein atoms to C and write in new file, adds cofactor to new file, writes ligand into xtal-lig.pdb, connects to the db to get ligand and cofactor information ***\n"
	print "Written by Agata Krasowski *a.krasowski@dundee.ac.uk*\n"
	print "Usage:   --help shows this help"
	print "         -fi [pdb_file] -fop [output file protein] -fol [output file ligand] -db [data base] -tb [data table] -user [username db] -password [password]"

	sys.exit()

#*******************************************************************************
# MAIN
#***************

pdb_file = open(sys.argv[2], 'r') #input file
out_file_protein= open(sys.argv[4],'w') #output file
out_file_ligand= open(sys.argv[6],'w')
pdb_code = str(sys.argv[2])[:-4] #changed to -4 by RB 13/07/10
out_file_cofactor = open(pdb_code+'_hetero.pdb','w')
out_file_protein_cofactor = open(pdb_code+'_volume.pdb','w') # for contact area calculation with sybyl
db = str(sys.argv[8])
tb = str(sys.argv[10])
us = str(sys.argv[12])
pw = str(sys.argv[14])
wantedpacode = str(sys.argv[15]) # Added 02/07/2012 - Aurijit Sarkar
wantedpdb = str(sys.argv[16])
wantedlig = str(sys.argv[17])
conn=mysql.connect2server(pw, us, db)  			    
cursor = conn.cursor ()
#db = 'dataset_0709'
command = "select lig, cof, metal from " + tb + " where id = '" + wantedpdb + "' and pacode = '" + wantedpacode + "' and lig = '" + wantedlig + "' limit 1"
print command
cursor.execute(command)
rows = cursor.fetchall ()

ligand = rows[0][0]
print ligand
cofactor = str(rows[0][1])
print cofactor
metal = str(rows[0][2])
print metal

#HETATM 4666 ZN    ZN A 701      43.821  38.240  46.712  1.00 25.11          ZN  
#HETATM 4667  O1  LPR A 702      40.291  33.743  45.120  1.00 13.04           O  
for i in pdb_file.readlines():

	if i[:4]=="ATOM": #These lines contain the relevant information
		outline="ATOM   "+i[7:11]+" "+ " CX" +"  "+"AAA"+""+i[20:54]+" \n"
		out_file_protein.write(outline)
		out_file_protein_cofactor.write(i)

	if i[:6]=="HETATM": #If structure contains cofactor, write it in pdb_output file
		if i[17:20] == cofactor:
                	outline="ATOM   "+i[7:11]+" "+ " CX" +"  "+"AAA"+""+i[20:54]+" \n"
			out_file_protein.write(outline)
			out_file_cofactor.write(i)
			out_file_protein_cofactor.write(i)
		if i[17:20] == ligand:# and (lignum == int(i[7:11]) or ligandos == False):
			outline = string.replace(i, 'HETATM', 'ATOM  ') #HETATM must be ATOM in xtal-lig.pdb
			#print outline
			outline = outline[:20]+'   '+outline[23:] #replace chain letter
			#print outline
			out_file_ligand.write(outline)
		if i[17:20] == ' '+metal:
			outline="ATOM   "+i[7:11]+" "+ " CX" +"  "+"AAA"+""+i[20:54]+" \n"
			out_file_protein.write(outline)	
			out_file_protein_cofactor.write(i)			

cursor.close()
conn.close()
out_file_ligand.close()
out_file_protein.close()
out_file_cofactor.close()
out_file_protein_cofactor.close()
sys.exit()
