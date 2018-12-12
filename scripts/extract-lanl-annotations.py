import csv, argparse, sys

arguments = argparse.ArgumentParser(description='Filter existing accession numbers from a TN93 output; write abbreviated file to stdout and diagnostics to stderr')

arguments.add_argument('-d', '--distances',   help='Input Must be a CSV file with three columns: ID1,ID2,distance.', required = True, action = 'append')
arguments.add_argument('-i', '--inject',   help='(FILE, INDEX, VALUE) For a subset of sequences with accessions listed in the FILE (one per line), set the value of the INDEX output field to VALUE', required = False, nargs = 3, action = 'append')

run_settings = arguments.parse_args()

writer = csv.writer (sys.stdout, delimiter = '\t')
writer.writerow (['ID', 'Country', 'IsolateYear', 'Subtype'])
already_done = set ()

override = {}


if run_settings.inject:
    for [file, index, value] in run_settings.inject:
        with open (file, 'r') as fh:
            for l in fh:
                lid = l.strip()
                if lid not in override:
                    override[lid] = [lid, None, None]

                override[lid][int(index)] = value
                

for d in run_settings.distances:
    with open (d) as fh:
        read_distances = csv.reader (fh, delimiter = ',')
        next (read_distances)
        for line in read_distances:
            for id in [line[0], line[1]]:
                if id not in already_done:
                    pieces = id.split ('.')
                    if len (pieces) >= 6:
                        acc = pieces[-1]
                        piece1 = override[acc][1] if acc in override and pieces[1] == '-' else None
                        piece2 = override[acc][2] if acc in override and pieces[2] == '-' else None
                        piece1 = piece1 if piece1 else pieces[1]
                        piece2 = piece2 if piece2 else pieces[2]
                        writer.writerow  ([id, piece1, piece2, pieces[0]])
                        #if (id == 'B.US.2011.505_0840a.WG09.505_0840.MG196836'):
                        #    print ('HAI', id.split ('.'), len (id.split ('.')) >= 6)
                        #    sys.exit (0)
                    already_done.add (id)
        
            
        
            
            
