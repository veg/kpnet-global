""" This script takes the JSON file output by hivnetworkcsv and adds the
data dictionary for subject attributes to create an annotated JSON suitable
for rendering by hivtrace-viz (https://github.com/veg/hivtrace-viz)

Author:
    Sergei L Kosakovsky Pond (spond@temple.edu)

Version:
    v1.0.0 (2017-05-09)
    v1.1.0 (2017-09-04) : added support for 'enums', fixed bugs

Example:

    Inject three standard attributes from the clinical JSON, print result to stdout::

        python3 python/inject-attributes.py -m ID-mapping/master-map.json -n data/20170330/network.json -a clinical/master.json -f Stage String '' -f EDI Date 'fulldate' -f ARV Date 'fulldate'

    Inject TNS print result to stdout::

        python3 python/inject-attributes.py -m ID-mapping/master-map.json -n data/20170330/network.json -t data/20170330/TNS.tsv -f "TNS" "Number" 'x: float(x) if x != "None" else 0.'

"""

import csv
import argparse
import sys
import json
import re
import datetime
import functools
from pirc_tools import *

def enum_mapper (key, dict):
    try:
        return dict[key]
    except KeyError:
        return None

#-------------------------------------------------------------------------------


arguments = argparse.ArgumentParser(description='Annoated the JSON file representing the PIRC network with data attributes from clinical data and isolation dates.')

arguments.add_argument  ('-o', '--output', help    = 'Output the annotated JSON network file to', nargs = '?', type = argparse.FileType('w'), default = sys.stdout)
arguments.add_argument  ('-n', '--network',   help    = 'The input network file to process', nargs = '?', type = argparse.FileType('r'), default = sys.stdin)
arguments.add_argument  ('-m', '--idmapper', help  = 'If desired, specify the JSON file providing ID conversion from legacy (or other study) identifiers, as a JSON file', required = False, type = argparse.FileType('r'))
arguments.add_argument  ('-x', '--missing', help  = 'If desired, provide a value to inject for nodes that do not have an attribute value specified', required = False, nargs = 2, action = 'append')
arguments.add_argument ('-X', '--clear', help = 'Flush existing attributes', required = False, action = 'store_true')
arguments.add_argument  ('-i', '--index',   help    = 'The name of the column that indexes records (patient ID)', type = str)
input_group = arguments.add_mutually_exclusive_group(required=True)
input_group.add_argument  ('-a', '--attributes',   help    = 'The JSON file with node attributes', type = argparse.FileType('r'))
input_group.add_argument  ('-t', '--tab',   help    = 'A TSV file with node attributes', type = argparse.FileType('r'))
input_group.add_argument  ('-c', '--csv',   help    = 'A CSV file with node attributes', type = argparse.FileType('r'))

arguments.add_argument ('-f', '--field', help = 'Describe an argument to be added to invididual nodes as "name" "label" "type" "transform"; currently supported types are "String", "enum", "Date", "Number"; transform must be specified as a lambda, an empty string to use an identity map, or a python style dict to specify an enum; "fulldate" is a predefined option to reformat the date using the default hivtrace-viz format', required = True, nargs = 4, action = 'append')

import_settings = arguments.parse_args()

network_json    = json.load (import_settings.network)

# set up record filtering

network_attribute_key = "patient_attribute_schema"
node_attribute_key    = "patient_attributes"
inject_missing_value  = import_settings.missing

ensure_key (network_json, network_attribute_key)

field_transformations = {}
field_names = {}
predefined_transforms = {'fulldate' : 's: datetime.datetime.strptime (s,"%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"'}

for key_pair in import_settings.field:
    network_json [network_attribute_key][key_pair[1]] = {'name' : key_pair[1], 'type': key_pair[2], 'label' : key_pair[1]}
    field_names [key_pair[0]] = key_pair[1]
    if key_pair[2] == 'enum':
        mapping = eval (key_pair[3])
        network_json [network_attribute_key][key_pair[0]]['type'] = "String"
        network_json [network_attribute_key][key_pair[0]]['enum'] = list (mapping.values())
        field_transformations [key_pair[0]] = functools.partial (enum_mapper, dict = mapping)
    else:
        if len (key_pair[3]) == 0 :
            field_transformations [key_pair[0]] = lambda x: x
        elif key_pair[3] in predefined_transforms:
            field_transformations [key_pair[0]] = eval ("lambda " + predefined_transforms[key_pair[3]])
        else:
            field_transformations [key_pair[0]] = eval ("lambda " + key_pair[3])


if import_settings.attributes: # JSON input
    to_import = json.load (import_settings.attributes)
else: # TSV import
    if import_settings.tab:
        csv_reader = csv.reader (import_settings.tab, delimiter = '\t')
    else:
        csv_reader = csv.reader (import_settings.csv, delimiter = ',')

    fields = next (csv_reader)
    
    index_on = 0
    if import_settings.index:
        index_on = fields.index (import_settings.index)
        if index_on < 0:
            raise "Invalid field to index on (%s)" % import_settings.index
    
    to_import = {}
    for line in csv_reader:
        to_import [line[index_on]] = {}
        for i, k in enumerate (line):
            if i != index_on:
                 to_import [line[index_on]][fields[i]] = k
                 
if import_settings.idmapper:
    mapper = json.load (import_settings.idmapper)
    inverse = inverse_map (mapper)

    def mapper_func (x):
        if type (x) == dict:
            x['id'] = mapper_func (x['id'])
        else:
            if x in inverse:
               return inverse[x]

        return x

    id_mapper = lambda x : mapper_func (x)
else:
    id_mapper = lambda x: x


nodes_indexed_by_id = {}
uninjected_set = set ()
for n in network_json ["Nodes"]:
    nodes_indexed_by_id [n['id']] = n
    uninjected_set.add (n['id'])
    if import_settings.clear:
        if node_attribute_key in n:
            del n[node_attribute_key]


for n, values in to_import.items():
    node_id = id_mapper (n)
    if node_id in nodes_indexed_by_id:
        node_dict = ensure_key (nodes_indexed_by_id[node_id], node_attribute_key)
        for k, val in values.items():
            if k in field_transformations:
                store_this = field_transformations[k] (val)
                if store_this is not None:
                    node_dict[field_names[k]] = store_this
                    if node_id in uninjected_set:
                        uninjected_set.remove (node_id)
                    
if inject_missing_value:
    for node_id in  uninjected_set:
        node_dict = ensure_key (nodes_indexed_by_id[node_id], node_attribute_key)
        for values in inject_missing_value:
            node_dict[values[0]] = values[1]


json.dump (network_json, import_settings.output, indent = 1)
