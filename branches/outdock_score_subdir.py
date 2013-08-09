#!/usr/bin/python

#extract scores out of outdock_file

import os,sys, string

if len(sys.argv) <> 2:
	print 'outdock_score_subdir.py <docking results (chunks) dir-prefix>'
	sys.exit()

#Number of Subdirecotries


s_prefix = sys.argv[1]
if not s_prefix [-1] == '_':
	s_prefix += '_'

s_mdb = s_prefix[:-1] + '.mdb'

number_dir = 0
for i in os.listdir('.'):
	#print i
	if s_prefix in i:
		number_dir += 1
zaehler = 1
print number_dir , ' zahl der dir'

if not os.path.exists(s_mdb):
	os.mkdir(s_mdb)


#out_file = open (sys.argv[2], 'w') 
out_file12 = open ('scores12.txt', 'w')
#----------------------
def score_sort(a,b):
   if a[1] < b[1] :
     return -1
   elif a[1] == b[1]:
     return 0
   else:
     return 1
#----------------------


     

dict = {}

total_list = []

while zaehler <= number_dir:
  print zaehler
  os.chdir(s_mdb)
  command = '/homes/asarkar/DrugPred2.1/dock2mol2_high_scoring.py ../' + s_prefix + str(zaehler) + '/*.eel1'
  print command
  os.system(command)
  os.chdir('..')
  file_name = s_prefix + str(zaehler) + '/OUTDOCK'
  print '=========> open ' + file_name + ' <==============='
  read_file = open(file_name, 'r')
  right = False
  for i in read_file.readlines():
  	if (i[0:6] == '     E') and (string.strip(i[72:79]) == 'Total'):  #start of docking results in OUTDOCK
    		right = True

	if (i[0:6] <> ' Array') and (i[0:6] <> 'databa') and (i[0:6] <> '     E' and right == True and i[0:6] <> ' EOF: '):
    		name1 = i[7:16]
   		nhvy = float( string.strip( i[39:41] ) )
    
 	if (i[0:6] == '     E') and (string.strip(i[72:79]) <> 'Total'):
  		name2 = i[7:16]
   		vdw   = float( string.strip( i[42:48] ) )
  		if name1 == name2:
     			score = vdw/nhvy
			#print score
      			
			if score <= -float(1.2):
      				out_file12.write(name1 + '\t' + str(nhvy) + '\t' + str(vdw) + '\t' + str(score) +'\n')


	if (i[0:6] == ' EOF: '): #end of docking results in OUTDOCK
     		right = False
		break	
	
  zaehler = zaehler + 1
  read_file.close()
  
  
#out_file1.close()
out_file12.close()
#out_file15.close()


