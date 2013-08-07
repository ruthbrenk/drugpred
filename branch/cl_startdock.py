#!/usr/bin/python

#run as array job
#if files are bzipped -> copy to local disk and unzip there


import os,sys

db_dir = sys.argv[1]

zipped = sys.argv[2] #are files bzipped?

if zipped == 'True':
	zipped = True
else:
	zipped = False

files = os.listdir(db_dir)


file = '#$ -S /bin/tcsh\n#$ -cwd\n#$ -V\n'
path = os.getcwd()

counter = 1
for i in files: #set up all sub dirs with correct input files
	if i[-2:] == 'db' or 'z2':
		
		sub_dir = 'acd_' + str(counter)
		if not os.path.exists(sub_dir):
			os.system('mkdir ' + sub_dir)

		os.chdir(path + '/' + sub_dir)

		os.system('cp ../INDOCK .')
		command = 'ln -s ' + db_dir +  i + ' db_file'
		print command
		os.system(command)

		counter = counter + 1
		os.chdir('..')

#create file to submit array job
start_file = open('start_dock.bin', 'w')
start_file.write(file)
start_file.write('cd acd_$SGE_TASK_ID\n')
if zipped: #files must be unzipped, to save diskspace to do this on temporary cluster disk, $TMPDIR 
	start_file.write('ls -larth *\n') #save name of db file that should be docked
	start_file.write('cp db_file $TMPDIR/db_file.db.bz2\n')
	start_file.write('bunzip2 $TMPDIR/db_file.db.bz2\n')
	start_file.write('unlink db_file\n')
	start_file.write('ln -s $TMPDIR/db_file.db db_file\n')
start_file.write('/software/dockenv/bin/Linux/dock_vol.test\n')
if zipped:
	start_file.write('unlink db_file\n')
start_file.write('rm -f *.1')
start_file.close()

os.system('chmod 755 start_dock.bin')
os.system('qsub -q 64bit-pri.q,64bit.q -t 1-' + str(counter-1) + ' start_dock.bin')
