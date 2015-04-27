#!/usr/bin/env python

import xmlrpclib
import platform
import shutil
import sys
import os, os.path
import glob
from copy import copy
from os.path import join as j

usage = """

"""

server = xmlrpclib.ServerProxy('http://cfe1019692:8080')

if 'Darwin' in platform.system():
	genomics_path = "/Volumes/dna/gnome2/CFSANgenomes"
elif 'Linux' in platform.system():
	genomics_path = "/shared/gn2/CFSANgenomes"
else: #Windows
	genomics_path = "Z:/CFSANgenomes"
	
if __name__ == '__main__':
	
	if '-h' in sys.argv:
		print usage
		quit()
		
	pipe = False
	
	if '-' in sys.argv:
		sys.argv.remove('-')
		pipe = True
		
	if pipe:
		ids = [s.replace("\n","") for s in sys.stdin.readlines()]
	else:
		ids = sys.argv[1:]
		
	for id in ids:
		record = server.get(id)
		if 'Runs' not in record:
			record['Runs'] = (record, )
		for run in record['Runs']:
			if run['RawFile']:
				for fname in run['RawFile'].split(','):
					for fpath in glob.glob(j(genomics_path, record['FdaAccession'], run['RunID'], fname)):
						print fpath