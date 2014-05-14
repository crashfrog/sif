#!/usr/bin/env python

import sys
import xmlrpclib

server = xmlrpclib.ServerProxy('http://cfe1019692:8080')

if __name__ == '__main__':
	pipe = False
	fields = ['FdaAccession', 'Genus', 'Species', 'StrainName']
	if '-' in sys.argv:
		sys.argv.remove('-')
		pipe = True
		
	for arg in sys.argv[1:]:
		if '--' in arg:
			fields.append(sys.argv.pop(sys.argv.index(arg)).replace('--', ''))
		
	if pipe:
		ids = [s.replace("\n","") for s in sys.stdin.readlines()]
	else:
		ids = sys.argv[1:]
		
	try:
		print '\t'.join(fields)
		for id in ids:
			iso = server.get(id)
			print '\t'.join([iso[key] for key in fields])
	except KeyError:
		print 'Unrecognized database field at isolate level. Acceptable fields are:',
		iso = server.get('CFSAN000001')
		del iso['Runs']
		print iso.keys()