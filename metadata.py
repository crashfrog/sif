#!/usr/bin/env python

import sys
import xmlrpclib

import functools
from collections import defaultdict

usage = """Version 0.2

	metadata <cfsan number>[...] -<field_name>[...] [--Alias={<field_name}]

	Quick and dirty table tool. Takes as input a list of CFSAN numbers, options
	are CFSAN database field names (single dash) or 'rename' expressions
	
	Examples:
		metadata CFSAN001992 CFSAN001993 -Genus -Species -RunCell
		metadata CFSAN001992 --Organism="{Genus} {Species} subsp. {Subspecies}\
 serovar {Serovar} str. {StrainName}" -Isolate
		cat "CFSAN001992" | metadata - -Project


"""

keys_succeed = False

server = xmlrpclib.ServerProxy('http://cfe1019692:8080')

class NameableCallable(object):

	def __init__(self, name, func, exp):
		self.name = name
		self.func = func
		self.exp = exp
		
	def __str__(self):
		return self.name
		
	def __repr__(self):
		return self.exp
		
	def __call__(self, *args):
		return self.func(*args)


def retrieve(struct, key):
	if struct.get(key, False) == False:
		try:
			return key(struct)
		except TypeError:
			return struct[key]
		except KeyError:
			if keys_succeed:
				return ''
	else:
		return struct.get(key, '')


if __name__ == '__main__':
	
	if '-h' in sys.argv:
		print usage
		quit()
	pipe = False
	header = True
	fields = ['CFSAN']
	runs = 'all'
	if '-x' in sys.argv:
		sys.argv.remove('-x')
		header = False
		fields = list()
		
	if '-d' in sys.argv:
		sys.argv.remove('-d')
		header = True
	
	if '-f' in sys.argv:
		sys.argv.remove('-f')
		runs = 'first'
	if '-l' in sys.argv:
		sys.argv.remove('-l')
		runs = 'last'
	
	
	if '-' in sys.argv:
		sys.argv.remove('-')
		pipe = True
		
	for arg in sys.argv[1:]:
		if '--' in arg:
			name, exp = sys.argv.pop(sys.argv.index(arg)).replace('--', '').split('=')
			callable = NameableCallable(name, lambda i, exp=exp: exp.format(**i), exp)
			fields.append(callable)
			
		elif '-' in arg:
			fields.append(sys.argv.pop(sys.argv.index(arg)).replace('-', ''))
			
		
	if pipe:
		ids = [s.replace("\n","") for s in sys.stdin.readlines()]
	else:
		ids = sys.argv[1:]
		
	#ids = list(set(ids))
	#ids.sort()
		
	try:
		if header:
			print '\t'.join([str(f) for f in fields])
		for id in ids:
			iso = server.get(id)
			iso['CFSAN'] = iso['FdaAccession']
			try:
				l = [retrieve(iso, key) for key in fields]
				print '\t'.join(l)
			except (KeyError, TypeError) as e:
				#print '-=-=-=-=-',
				try:
					if iso['Runs']:
						if 'first' in runs:
							iso['Runs'] = (iso['Runs'][0], )
						elif 'last' in runs:
							iso['Runs'] = (iso['Runs'][-1], )
					else:
						
						d = defaultdict(lambda: " - ")
						d['RunID'] = iso['FdaAccession']
						#d.update(iso)
						iso['Runs'] = (d, )


					for run in iso['Runs']:
						run.update(iso)
						run['CFSAN'] = run['RunID']
						l = [retrieve(run, key) for key in fields]
						print '\t'.join(l)
				except Exception:
					print type(e), e
					for key in fields:
						print key, iso.get(key, type(key))
					raise
			#print '\n',
			keys_succeed = True
		
	except (KeyError, TypeError) as e:
		import pprint
		print usage
		print 'Unrecognized database field "{}". Acceptable fields are:'.format(str(e)),
		iso = server.get('CFSAN000001')
		run = iso['Runs'][0]
		del iso['Runs']
		pprint.pprint(sorted(iso.keys()))
		pprint.pprint(sorted(run.keys()))
		raise