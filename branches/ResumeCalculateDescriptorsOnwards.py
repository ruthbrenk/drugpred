#!/usr/bin/python
import os, sys, time

db = sys.argv[1]
datatable = sys.argv[2]
desctable = sys.argv[3]
uname = sys.argv[4]
password = sys.argv[5]
curr_dir = os.path.abspath('./')


### COPY ALL PROTEIN AND SUPERLIGAND FILES TO $PATH ###


command = '/homes/asarkar/DrugPred2.1/CalculateDescriptors.py ' + curr_dir + ' ' + ' ' + db + ' ' + datatable + ' ' + desctable + ' ' + uname + ' ' + password
os.system(command)
