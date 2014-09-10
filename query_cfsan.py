#!/usr/bin/env python

import xmlrpclib
import sys
import itertools

server = xmlrpclib.ServerProxy('http://cfe1019692:8080')

usage = """Version 0.1

Takes search terms as arguments and emits CFSAN RunID's or FdaAccessions that 
match the query. Useful as a

Usage:

	query_cfsan <field>__<relation> <query_term> [...][-limit <num_results>]
	
	(those are double underscores)
	
	'contains' and 'containsnot' use pattern-matching on fields
	'is' and 'isnot' take 'null' as a query term to include or exclude database
		nulls.
	
	Examples:
		
		query_cfsan Project__contains GenomeTrakr Genus__isnot Salmonella
		query_cfsan Serovar__containsnot Typhi Sequenced__is null

"""

if __name__ == '__main__':
	try:
		sys.argv[1]
	except IndexError:
		print usage
		quit()
		
	terms = list()
	limit = -1
	try:
		for term, pattern in itertools.izip(*[iter(sys.argv[1:])]*2):
			if '-limit' in term:
				limit = int(pattern)
			if '__containsnot' in term:
				field = term.split('__')[0]
				terms.append("([{}] NOT LIKE '%{}%')".format(field, pattern))
			elif '__contains' in term:
				field = term.split('__')[0]
				terms.append("([{}] LIKE '%{}%')".format(field, pattern))
			elif '__isnot' in term:
				if 'null' in pattern:
					field = term.split('__')[0]
					terms.append("([{}] IS NOT NULL)".format(field, pattern))
				else:
					field = term.split('__')[0]
					terms.append("([{}] != '{}')".format(field, pattern))
					
			elif '__is' in term:
				if 'null' in pattern:
					field = term.split('__')[0]
					terms.append("([{}] IS NULL)".format(field, pattern))
				else:
					field = term.split('__')[0]
					terms.append("([{}] = '{}')".format(field, pattern))
			
			
			elif '=' in term:
				if 'null' in pattern:
					field = term.split('=')[0]
					terms.append("([{}] IS NULL)".format(field, pattern))
				else:
					field = term.split('=')[0]
					terms.append("([{}] = '{}')".format(field, pattern))
		keys = server.query_cfsan(' AND '.join(terms) + ' ORDER BY [FdaAccession]')[0:limit]
		for key in keys:
			run = server.get(key)
			print run.get('RunID', run['FdaAccession'])
			
			
	except (IndexError):
		print usage
		quit()
			