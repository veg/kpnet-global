import csv, argparse, sys, json
from Bio import SeqIO

arguments = argparse.ArgumentParser(description='Extract a cluster by ID')

arguments.add_argument('-j', '--json',   help='The JSON file', required = True)
arguments.add_argument('-c', '--cluster',   help='The cluster ID', required = True, type = int)
arguments.add_argument('-t', '--type',   help='Node type', required = False, type = str)
arguments.add_argument('-f', '--fasta',  help='FASTA files for seqeunce extraction', type = str, action = 'append')

run_settings = arguments.parse_args()

with open (run_settings.json, "r") as fh:
    network = json.load (fh)

nodes = set ()

for i,n in enumerate (network["Nodes"]):
    if (n["cluster"] == run_settings.cluster):
        if run_settings.type:
            if n["patient_attributes"]["Source"] != run_settings.type:
                continue
        nodes.add (n["id"])


if run_settings.fasta:
    for ff in run_settings.fasta:
        with open(ff, "r") as fh:
            for record in SeqIO.parse(fh, "fasta"):
                if record.id in nodes:
                    print (">%s\n%s\n" % (record.id, str (record.seq)))
else:
    for n in nodes:
        print (n)





