import csv, argparse, sys, json, random
from Bio import SeqIO

arguments = argparse.ArgumentParser(description='Extract a cluster by ID')

arguments.add_argument('-j', '--json',   help='The clustered JSON file', required = True)
arguments.add_argument('-w', '--whitelist',   help='The file with the list of sequence IDs that MUST be included', required = True, type = str)
arguments.add_argument('-size', '--size', help = 'The number of sequences to include', required = False, type = int, default = 250)
arguments.add_argument('-f', '--fasta',   help='FASTA files for sequences', type = str, action = 'append')

run_settings = arguments.parse_args()

with open (run_settings.whitelist, "r") as fh:
    whitelisted = set()
    for line in fh:
        whitelisted.add (line.rstrip())



#centroid" : ">BC.CN.2013.kang217.-.KJ401559\n
def extract_year (record):
    id = None
    try:
        id = record.split ("\n")[0][1:]
        pieces = id.split ('.')
        if len (pieces) >= 2:
            return (id, int (pieces[2]))
    except:
        return (id, None)

    return (id, None)

with open (run_settings.json, "r") as fh:
    clusters = json.load (fh)

selected      = set ()

def report_selected (subset):
    for s in subset:
        print (s)

available_for_sampling_by_year = {}

left_to_draw = 0

for cluster in  clusters:
    is_whitelisted = True in [n in whitelisted for n in cluster["members"]]
    if is_whitelisted:
        selected.update (cluster["members"])
    else:
        id, year = extract_year (cluster["centroid"])
        if year not in available_for_sampling_by_year:
            available_for_sampling_by_year[year] = set()
        available_for_sampling_by_year[year].add (id)
        left_to_draw += 1

if None in available_for_sampling_by_year and len (available_for_sampling_by_year) > 1:
    left_to_draw -= len(available_for_sampling_by_year[None])
    del available_for_sampling_by_year[None]

per_bin = (run_settings.size - len (selected)) // len (available_for_sampling_by_year)

keys = set (available_for_sampling_by_year.keys())

for year, seqs in available_for_sampling_by_year.items():
    if len (seqs) <= per_bin:
        selected.update (seqs)
        available_for_sampling_by_year[year] = set ()
        left_to_draw -= len (seqs)
        keys.remove (year)
    else:
    
        sample = random.sample (seqs, per_bin)
        selected.update ([seqs.pop() for k in range (per_bin)])
        left_to_draw -= per_bin

while len (selected) < run_settings.size and left_to_draw > 0:
    year = random.sample (keys, 1)[0]
    left_to_draw -= 1
    selected.add (available_for_sampling_by_year[year].pop())
    if len (available_for_sampling_by_year[year]) == 0:
        keys.remove (year)

if run_settings.fasta:
    for ff in run_settings.fasta:
        with open(ff, "r") as fh:
            for record in SeqIO.parse(fh, "fasta"):
                if record.id in selected:
                    print (">%s\n%s\n" % (record.id, str (record.seq)))
else:
    for s in selected:
        print (s)



#while len (

#for year, values in available_for_sampling_by_year.items():
#    print ("%s => %d" % (str(year), len (values)))








