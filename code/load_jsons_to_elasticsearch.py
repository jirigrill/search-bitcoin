"""imports"""
from pathlib import Path
import json
import hashlib
import os
from elasticsearch8 import Elasticsearch

# TODO: update all exceptions to proper types

# function taking document id as stting and returns hashed_id by md5
def create_document_hashed_id(document_id):
    """
    Takes id as parameter and returns hashed id
    """
    m = hashlib.md5()
    document_id = document_id.encode('utf-8')
    m.update(document_id)
    hashed_id = str(int(m.hexdigest(), 16))[0:12]
    return hashed_id


# creates client for elasticsearch
_es = Elasticsearch(os.getenv('BTCTRANSCRIPTS_SERVER_URI'), basic_auth=(os.getenv('BTCTRANSCRIPTS_USERNAME'),os.getenv('BTCTRANSCRIPTS_PASSWORD')))

# iterates over *.json files in processed_files directory and adds them to index
files = Path(os.getenv('BTCTRANSCRIPT_OUTPUT_FOLDER')).glob('*.json')
for file in files:
    transcript_json = json.load(open(file, encoding='UTF-8'))
    TRANSCRIPT_ID = create_document_hashed_id(transcript_json['title']+' '+transcript_json['language'])

    print(f"upload of file {file}")
    try:
        resp = _es.index(index='btctranscripts', id = TRANSCRIPT_ID, document=transcript_json)
        print(f"elastic response: {resp['result']}")
    except Exception:
        print(f"upload of {file} wasnt successful")
