import csv, argparse, sys, re
from Bio import SeqIO

arguments = argparse.ArgumentParser(description='Filter existing accession numbers from a FASTA file; write filtered file to stdout')

arguments.add_argument('-i', '--info',       help='A CSV file with the SECOND column containing accession numbers to exclude', required = True )
arguments.add_argument('-f', '--fasta',      help='FASTA file with LANL sequences', required = True)
arguments.add_argument('-e', '--extractor',      help='Regxp with a named subexpression (ACC) to extract accession numbers from sequence headers', required = False, default = '^.+\\.(?P<ACC>[\w]+)$')

run_settings = arguments.parse_args()

existing_accessions = set ()

with open (run_settings.info, "r") as fh:
    reader = csv.reader (fh, delimiter = ',')
    next (reader)
    for line in reader:
        existing_accessions.add (line[1].upper ())

print ("Read %d blacklisted accession numbers" % len (existing_accessions), file = sys.stderr)

sequence_data = SeqIO.parse(run_settings.fasta, "fasta")

extractor = re.compile (run_settings.extractor)

all_skipped = 0

for seq in sequence_data:
    acc = extractor.search (seq.name).group ('ACC')
    if acc in existing_accessions:
        print ("Skipping %s" % seq.name, file = sys.stderr)
        all_skipped += 1
    else:
        print (">%s\n%s\n" % (seq.name, str (seq.seq)))

print ("Filtered %d sequences" % all_skipped, file = sys.stderr)
