#!/usr/bin/env python

import xmlrpclib
import sys
import datetime

server = xmlrpclib.ServerProxy('http://cfe1019692:8080', use_datetime=True)

usage = """Version 0.3

Usage:

	seq_stat <CFSAN isolate or run number> {<another number> <yet another number...}
	
	Return useful information about the sequencing, QA, and assembly status of
	an isolate.
	
	v0.1:	first working version
	 0.2:	added PGAP annotation information, where known
	
	Options:
	-h	Show this help.
	-p	Operate in pipe mode - search each line of input on STDIN.

"""

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def main(argv):
	for s in argv:
		struct = server.get(s)
		if 'Salmonella' in struct['Genus']:
			print "+{:.<79}".format("{FdaAccession}: {Genus} {Species} {Subspecies} {Serovar} str. {StrainName}".format(**struct))
		else:
			print "+{:.<79}".format("{FdaAccession}: {Genus} {Species} {StrainName}".format(**struct))
		if 'PRJNA' not in struct['NCBI_BioProject'] and struct['NCBI_BioProject']:
			struct['NCBI_BioProject'] = 'PRJNA' + struct['NCBI_BioProject']
			
		print "|{NCBI_BioProject:<20}{NCBI_BioSample}".format(**struct)
		
		if 'Runs' in struct:
			#struct is an isolate
			
			#print some pretty text!
			if struct['Runs']:
				for run in struct['Runs']:
					print "|+{RunID:<15}{SequenceRunDate:>30}{SequencingTechnology:>33}".format(**run)
					if run['Issues']:
						import textwrap
						for line in textwrap.wrap(run['Issues'], width=75):
							print "#  {:<77}#".format(line)
					for job in server.query_jobs('qualities', "accession='{RunID}'".format(**run)):
						print "||+Quality: {file_root} {status}".format(**job)
						if 'finished' in job['status']:
							job['average_read_length'] = job['average_read_length'].replace("\n", '')
							try:
								print "|||{average_read_length} bases, avg/read, {num_reads:>7} reads, {size}".format(size = sizeof_fmt(int(job['file_size'])), **job)
							except:
								print "|||{average_read_length} bases, avg/read".format(**job)
					if run['AssemblyVersion']:
						print "||MainAssembly: {AssemblyVersion} {AssemblyFileName}".format(**run)
					for job in server.query_jobs('assemblies', "accession='{RunID}'".format(**run)):
						print "||+Assembly: {assem} {status}:".format(assem = job['assembly_version'] or job['job_type'], **job)
						if "finished" in job['status'] or "collected" in job['status']:
							try:
								elapsed = job['dateCompleted'] - job['dateStarted']
								print "|||{fasta_file} ({elapsed} h/m/s to asm) N50: {n50} Contigs: {num_contigs}".format(elapsed=elapsed, **job)
							except TypeError:
								print "|||{fasta_file} N50: {n50} Contigs: {num_contigs}".format(**job)
						if job['exception_note']:
							import textwrap
							for line in textwrap.wrap(job['exception_note'], width=75):
								print "#  {:<77}#".format(line)
					for job in server.query_jobs('jobs', "accession='{RunID}' AND job_type='PGAP Submission'".format(**run)):
						print "||+Annotation: {status} {date_completed}".format(**job)
						if 'error' in job['status']:
							import textwrap
							for line in textwrap.wrap("<{}>: {}".format(job['result_type'], job['result_value']), width=75):
								print "#  {:<77}#".format(line)
					
					print "||SRA:{NCBI_SraSubmission:<10}{NCBI_SraHupStatus:<10} {NCBI_SraSubmissionDate:<10}  WGS:{NCBI_WgsAccession:<16} {NCBI_WgsHupDate:<19}".format(**run)
				
				for job in server.query_jobs('assemblies', "accession='{FdaAccession}'".format(**struct)):
					print "|+Assembly: {assem} {status}:".format(assem = job['assembly_version'] or job['job_type'], **job)
					if "finished" in job['status'] or "collected" in job['status']:
						try:
							elapsed = job['dateCompleted'] - job['dateStarted']
							print "||{fasta_file} ({elapsed}) N50: {n50} Contigs: {num_contigs}".format(elapsed=elapsed, **job)
						except TypeError:
							print "||{fasta_file} N50: {n50} Contigs: {num_contigs}".format(**job)
					if job['exception_note']:
						import textwrap
						for line in textwrap.wrap(job['exception_note'], width=75):
							print "#  {:<77}#".format(line)
				
				for job in server.query_jobs('jobs', "accession='{FdaAccession}' AND job_type='PGAP Submission'".format(**struct)):
						print "||+Annotation: {file_root} {status} {date_completed}".format(**job)
						if 'error' in job['status']:
							import textwrap
							for line in textwrap.wrap("<{}>: {}".format(job['result_type'], job['result_value']), width=75):
								print "#  {:<77}#".format(line)
								
			else:
				#not run
				print 'not yet run.'
				
		else:
			#struct is a single run
			print "|+{RunID:<15}{SequenceRunDate:>30}{SequencingTechnology:>33}".format(**struct)
			for job in server.query_jobs('qualities', "accession='{RunID}'".format(**struct)):
				print "|+Quality: {file_root} {status}".format(**job)
				if 'finished' in job['status']:
					job['average_read_length'] = job['average_read_length'].replace("\n", '')
					print "||{average_read_length} bases, {num_reads:>7} reads, {size}".format(size = sizeof_fmt(int(job['file_size'])), **job)
			for job in server.query_jobs('assemblies', "accession='{RunID}'".format(**struct)):
				print "||+Assembly: {assem} {status}:".format(assem = job['assembly_version'] or job['job_type'], **job)
				if "finished" in job['status'] or "collected" in job['status']:
					try:
						elapsed = job['dateCompleted'] - job['dateStarted']
						print "|||{fasta_file} ({elapsed})".format(elapsed=elapsed, **job)
					except TypeError:
						print "|||{fasta_file}".format(**job)
				if job['exception_note']:
					import textwrap
					for line in textwrap.wrap(job['exception_note'], width=75):
						print "#  {:<77}#".format(line) 
			
			print "||SRA:{NCBI_SraSubmission:<10}{NCBI_SraHupStatus:<10} {NCBI_SraSubmissionDate:<10}  WGS:{NCBI_WgsAccession:<16} {NCBI_WgsHupDate:<19}".format(**struct)

		

try:
	if '-h' in sys.argv:
		print usage
		quit()
	if '-p' in sys.argv:
		sys.argv.remove('-p')
		[sys.argv.append(s.replace("\n", "")) for s in sys.stdin.readlines()]
	sys.argv[1] #try and provoke IndexError, in case no arguments given
	main(sys.argv[1:])
except IndexError:
	print usage
except Exception:
	#print sys.argv
	raise