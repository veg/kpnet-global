F=clusters/$1
S=$3

mkdir $F
python3 scripts/extract-cluster.py -j results/network.json  -c $2 -f data/kp-aligned.fas -f data/reference-aligned-filtered.fas > ${F}/sequences.fas
python3 scripts/extract-cluster.py -j results/network.json  -c $2 -t NCC > ${F}/ncc.txt
tn93-cluster -f -a RYWSMK -g 0.05 -l 500 -t 0.005 -c all -m json ${F}/sequences.fas > ${F}/dense-clusters.json
python3 scripts/subset-cluster.py -j ${F}/dense-clusters.json -w ${F}/ncc.txt -s $3 -f data/kp-aligned.fas -f data/reference-aligned.fas > ${F}/subset-${S}.fas
FastTree -nt < ${F}/subset-${S}.fas > ${F}/subset-${S}.tree
