#!/usr/bin/python
import os, sys, time

db = sys.argv[1]
datatable = sys.argv[2]
desctable = sys.argv[3]
uname = sys.argv[4]
password = sys.argv[5]
pacode = sys.argv[6]
wantedpdb = sys.argv[7]
wantedlig = sys.argv[8]
curr_dir = os.path.abspath('./')

### RUN AGATA'S AUTODOCK_CLUSTER1.PY ###
#command = 'qsub /homes/asarkar/AgataDockingScripts3/autoDock_cluster1.py' + ' ' + db + ' ' + datatable + ' ' + uname + ' ' + password + ' ' + curr_dir
command = 'qsub -V -cwd /homes/asarkar/DrugPred2.1/autoDock_cluster1.py ' + db + ' ' + datatable + ' ' + uname + ' ' + password + ' ' + curr_dir + ' ' + pacode + ' ' + wantedpdb + ' ' + wantedlig
os.system(command)

### wait for qsubbed jobs to finish ###

