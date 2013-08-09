#!/usr/bin/python

import os, sys, time

db = str(sys.argv[1])
tb = str(sys.argv[2])
us = str(sys.argv[3])
pw = str(sys.argv[4])

auri_path = sys.argv[5]

wantedpacode = sys.argv[6]
wantedpdb = sys.argv[7]
wantedlig = sys.argv[8]

path = os.path.abspath(auri_path)
print path + ' path'
os.chdir(path)

files = os.listdir('./')
files.sort()
log_array = []
counter = 0
for file_ in files:
        if file_[-4:] == '.pdb':
	#if file_ == '1fth.pdb': #'3f0r.pdb' or file_ =='2a6h.pdb' or file_ =='1t41.pdb' or file_ =='1t03.pdb' or file_ =='1rp7.pdb' or file_ =='1qij.pdb' or file_ =='1qbs.pdb' or file_ =='1q9m.pdb' or file_ =='1pxx.pdb' or file_ =='1ptw.pdb' or file_ =='1oyn.pdb' or file_ =='1nny.pdb' or file_ =='1nlj.pdb' or file_ =='1mwe.pdb' or file_ =='1kzn.pdb' or file_ =='1kts.pdb' or file_ =='1jf7.pdb' or file_ =='1iep.pdb' or file_ =='1hwl.pdb' or file_ =='1hw9.pdb' or file_ =='1hvr.pdb' or file_ =='1gu1.pdb' or file_ =='1ezq.pdb':
		os.chdir(path)
		pdb_code = file_[:-4]
		print file_
		print pdb_code+ ' pdb_code'
		if not os.path.exists(pdb_code):
			os.makedirs(pdb_code)
		os.chdir(pdb_code)	# cd in new directory and do docking stuff
		os.makedirs('docking')
		os.chdir('docking')

		#but first copy the right pdb file in dir
		command= 'cp ../../' + file_ + ' .'
		print command
		os.system(command)

		#create pdb, cofactor and ligand file
		command = 'python /homes/asarkar/DrugPred2.1/setPDBatomsC.py -fi ' + file_ + ' -fop '  + pdb_code + '_C.pdb -fol xtal-lig.pdb -db ' + db + ' -tb ' + tb + ' -user '+ us +' -password ' + pw + ' ' + wantedpacode + ' ' + wantedpdb + ' ' + wantedlig
		print command
		os.system(command)
		
		command = 'touch xtal-lig.mol2' 
		os.system(command)

		#if cofactor change to mol2
		try:
			command = '/software/babel/babel -ipdb '+pdb_code+'_hetero.pdb -omol2 ' +pdb_code+'_hetero.mol2 -e'
			os.system(command)
		except:
			print 'no cofactor'
		
		#create rec.amb
		command = '/software/dockenv/for_make_file/pdb2amb.py ' + pdb_code + '_C.pdb rec.amb'
		print command
		os.system(command)

		#create link from rec.amb to rec.pdb
		command = 'ln -s rec.amb rec.pdb'
		print command
		os.system(command)

		#install Make_dock_1x write output in temp.log
		command = 'make install -f /software/dockenv/for_make_file/Make_dock_lx'
		print command
		os.system(command)


		#copy  prot.table.ambcrg.ambH and amb.crg.oxt into grids
		command = 'cp /homes/asarkar/DrugPred2.1/amb.crg.oxt grids/.' 
		print command
		os.system(command)
		command = 'cp /homes/asarkar/DrugPred2.1/prot.table.ambcrg.ambH grids/.' 
		print command
		os.system(command)
	
			
		#make all write output in temp.log and attach temp.log to out.log 

		command = 'make all -f /software/dockenv/for_make_file/Make_dock_lx'
		print command
		os.system(command)
			
		#RB took solvmap out, not needed 15/07/2010	
		#cd in grids and solvmap
		#os.chdir('grids')
		#command = 'solvmap'
		#print command
		#os.system(command)
