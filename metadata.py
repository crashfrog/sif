#!/usr/bin/env python

import sys
import xmlrpclib

import functools

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
				for key in fields:
					if iso.get(key, False) == False:
						key(iso)
					else:
						iso.get(key, '')
				for key in fields:
					if iso.get(key, False) == False:
						#print repr(key)
						print key(iso), '\t',
					else:
						print iso.get(key, ''), '\t',
				#print '\t'.join([iso.get(key, False) or key(iso) for key in fields])
				print '\n',
			except (KeyError, TypeError) as e:
				#print '-=-=-=-=-',
				try:
					if iso['Runs']:
						if 'first' in runs:
							iso['Runs'] = (iso['Runs'][0], )
						elif 'last' in runs:
							iso['Runs'] = (iso['Runs'][-1], )

					for run in iso['Runs']:
						run = server.get(run['RunID'])
						run['CFSAN'] = run['RunID']
						for key in fields:
							if run.get(key, False) == False:
								print key(run), '\t',
							else:
								print run.get(key, ''), '\t',
						#print '\t'.join([run.get(key, False) or key(run) for key in fields])
						print ''
				except Exception:
					print type(e), e
					for key in fields:
						print key, iso.get(key, type(key))
					raise
			#print '\n',
		
	except (KeyError, TypeError) as e:
		import pprint
		print usage
		print 'Unrecognized database field "{}". Acceptable fields are:'.format(str(e)),
		iso = server.get('CFSAN000001')
		run = iso['Runs'][0]
		del iso['Runs']
		pprint.pprint(iso.keys())
		pprint.pprint(run.keys())