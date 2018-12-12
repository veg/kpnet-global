"""A few shared objects/defs.

Consistent definitions of sequence formatting,
JSON headers.

Author:
    Sergei L Kosakovsky Pond (spond@temple.edu)

Version:
    v1.0.0 (2015-11-20)


"""

from os import path

import bz2
import tempfile
import json
import sys
import os

__all__ = ["compose_label", "fields", "update_json", "inverse_map", "tagged_fields", "merge_equivalent","ensure_key"]

#-------------------------------------------------------------------------------
def inverse_map (dict):
    inverse = {}
    for k, v in dict.items():
        for a in v:
            inverse[a] = k
    return inverse

def compose_label (components, expected_fields):
    return '|'.join ([components[field] if field in components and type (components[field]) == str else 'NULL' for field in expected_fields])

def merge_equivalent (json, mapping_function):
    json_out = {}

    for id, record in json.items():
        mapped_id = mapping_function(id)
        if mapped_id in json_out:
            for seq_id, seq_record in record.items():
                json_out[mapped_id][seq_id] = seq_record
        else:
            json_out[mapped_id] = record

    return json_out

def ensure_key (d,key,value = None):
    if key not in d:
        if value is None:
            d[key] = {}
        else:
            d[key] = value
            

    return d[key]

#-------------------------------------------------------------------------------

def update_json (json_object, file_name):

    file_directory = path.dirname(path.abspath(file_name))

    if path.isfile (file_name): # need to archive and compress
        with open (file_name, 'r') as existing:
            old_json = json.load (existing)
            old_json = json.dumps (old_json)

        print ("Compressing existing JSON object to a temporary file", file = sys.stderr)
        temp_file = tempfile.mkstemp(suffix=".bz2", prefix="pirc_db", dir=file_directory)[0]
        os.write (temp_file, bz2.compress (bytes(old_json, 'UTF-8')))
        os.close(temp_file)


    with open (file_name, 'w') as json_dump:
        json.dump (json_object, json_dump, sort_keys=True, indent=1)


fields = ['id', 'date', 'gene', 'source', 'method', 'clone', 'lab', 'tag', 'comment']
tagged_fields = {'id' : 'id', 'date' : 'date'}
