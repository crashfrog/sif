#!/usr/bin/env python

import xmlrpclib
import sys

server = xmlrpclib.ServerProxy("http://cfe1019692:8080")

usage = """Version 0.2

Usage:

	find_cfsan <identifying string> {<another string} {a third string} ...
	
	"identifying string" can be almost anything we use to uniquely identify
	strains in the Genomics (BioNumerics) DB.
	
	Options:
	-h	Show this help.
	-	Operate in pipe mode - search each line of input on STDIN.

"""

try:
	if '-h' in sys.argv:
		print usage
		quit()
	if '-p' in sys.argv:
		sys.argv.remove('-p')
		[sys.argv.append(s.replace("\n", "")) for s in sys.stdin.readlines()]
	if '-' in sys.argv:
		sys.argv.remove('-')
		[sys.argv.append(s.replace("\n", "")) for s in sys.stdin.readlines()]
	sys.argv[1]
	for s in sys.argv[1:]:
		if s:
			m = server.find_cfsan(s)
			if m:
				#for r in m:
				#	print r
				print m
			else:
				sys.stderr.write("{} not found.\n".format(s))
				sys.stderr.flush()
except IndexError:
	print usage
except Exception:
	print sys.argv
	raise