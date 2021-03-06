#!/usr/bin/env python

import xmlrpclib
import platform
import shutil
import sys
import os, os.path
import glob
from copy import copy
from os.path import join as j

server = xmlrpclib.ServerProxy('http://cfe1019692:8080')



usage = """
add_run 0.2
Justin Payne
Feb 5, 2015

usage:
	add_run <CFSAN#> [options] [<file1> [<file2>]] [options]
	
options:
	-t <type>		: type of run (pacbio, iontorrent, 454, *miseq*, nextseq, hiseq)
	-<Field>=<Value>: edit created run record after processing by setting <Field> to <Value>
	-x				: don't try to copy anything.
	-p				: practice mode (doesn't commit)
	
"""

params = (('-t', 'type'), 
		#('param', 'varname'), 
		 )
		 
flags = (('-x', 'nocopy'),
		 ('-p','practice'),
		#('flag','varname'),
		) 
		 
type = 'miseq'
		 
post_load_updates = {}

run_types = {'pacbio':'PacBio RS sequence',
			 'miseq':'Illumina MiSeq sequence',
			 'iontorrent':'IonTorrent PGM sequence',
			 '454':'Roche 454 sequence',
			 'nextseq':'Illumina NextSeq sequence',
			 'hiseq':'Illumina HiSeq sequence',
			 }
			 
def trimmer(run_type):
	if 'MiSeq' in run_type:
		return 'basic_trimmer'
	else:
		return 'no_trimmer'

if 'Darwin' in platform.system():
	genomics_path = "/Volumes/dna/gnome2/"
elif 'Linux' in platform.system():
	genomics_path = "/shared/gn2/"
else: #Windows
	genomics_path = "Z:/"
	
def remove_either(l, a, b):
	try:
		l.remove(a)
	except ValueError:
		l.remove(b)
	
if __name__ == '__main__':
	
	try:
		for flag, value in params:
			if flag in sys.argv or ('--' + value in sys.argv):
				globals()[value] = sys.argv.pop(sys.argv.index(flag) + 1)
				remove_either(sys.argv, flag, '--' + value)
		for flag, value in flags:
			globals()[value] = False
			if flag in sys.argv or ('--' + value in sys.argv):
				globals()[value] = True
				remove_either(sys.argv, flag, '--' + value)
		for field_param in copy(sys.argv[1:]):
			if '-' in field_param[0]:
				field, value = field_param[1:].split('=')
				post_load_updates[field] = value
				sys.argv.remove(field_param)
	
		id = sys.argv.pop(1)
	except IndexError:
		print usage
		quit()
	try:
		session_key = server.open_deferred_accept('', {}, False)
		files = copy(sys.argv[1:])
		if not nocopy:
			if not files:
				files = glob.glob(id + '*fastq*')
			if not files:
				print "No files found to associate."
				server.deferred_accept_rollback(session_key)
				print usage
				quit()
			for file in files:
				with open(file, 'r') as file:
					#try to pre-emptively throw IO errors
					pass
		run_type = run_types[type]
		
		runid, path = server.deferred_accept(id, {'data_type':run_type,
												  'job_type':'SPAdes',
												  'trimmer':trimmer(run_type),
												  'raw_file':','.join([os.path.basename(f) for f in files]),
												  'file0':''.join(files[0:1]),
												  'file1':''.join(files[1:2]),
												  'assemble':'PacBio' not in run_type,
												  'status':'priority'}, session_key)
		print "{} created for {}".format(runid, id),
		sys.stdout.flush()
		dest_path = j(genomics_path, path)
		if not os.path.exists(dest_path) and os.path.exists(genomics_path) and not practice:
			os.makedirs(j(genomics_path, path))
		elif not os.path.exists(genomics_path):
			raise Exception("Genomics path can't be found.")
		for file in files:
			print ", {} copied to {}".format(file, dest_path),
			sys.stdout.flush()
			shutil.copyfile(file, j(dest_path, os.path.basename(file)))
		print "."
	except:
		print "Server rolling back on exception:"
		server.deferred_accept_rollback(session_key)
		raise
	else:
		try:
			if practice:
				print "Practice run, rolling back"
				raise Exception()
			server.close_deferred_accept(session_key)
			key = server.get(runid)['KEY']
			for field, value in post_load_updates.items():
				server.update_cfsan(key, field, value)
		except:
			server.deferred_accept_rollback(session_key)
			raise
			