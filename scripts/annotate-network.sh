F=$1

#import isolate years for KP data from data/kp-data.tsv; -X clears out all existing annotations
python3 scripts/inject-attributes.py -X -n ${F}.json -t data/kp-data.tsv  -f "IsolateYear" "Year" "Number" 'x: int(x)' -o network-annotated-temp.json
#import subtypes for KP data from data/kp-data.tsv; 
python3 scripts/inject-attributes.py -n network-annotated-temp.json  -t data/kp-data.tsv -f "Subtype" "Subtype" "String" ""  -o network-annotated-temp2.json
#import isolate years for LANL data from data/lanl-annotations.tsv
python3 scripts/inject-attributes.py -n  network-annotated-temp2.json -t data/lanl-annotations.tsv  -f "IsolateYear" "Year" "Number" 'x: None if x == "-" else int (x)' -o network-annotated-temp.json
#import country for LANL data from data/lanl-annotations.tsv; set country to 'US' by default for KP data
python3 scripts/inject-attributes.py -n  network-annotated-temp.json -t data/lanl-annotations.tsv  -f "Country" "Country" "String" 'x: None if x == "-" else x' -x "Country" "US"  -o network-annotated-temp2.json
#import subtype for LANL data from data/lanl-annotations.tsv
python3 scripts/inject-attributes.py -n  network-annotated-temp2.json -t data/lanl-annotations.tsv  -f "Subtype" "Subtype" "String" 'x: None if x == "-" else x' -o network-annotated-temp.json
#store the KP attribute for KP sequences and LANL for other sequences
python3 scripts/inject-attributes.py -n network-annotated-temp.json -t data/kp-data.tsv  -f "IsolateYear" "Source" "String" 'x: "NCC"' -x "Source" "LANL" -o ${F}.json

#remove temp files
rm network-annotated-temp*json
