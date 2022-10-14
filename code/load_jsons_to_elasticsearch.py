from hashlib import md5
from urllib import request
from elasticsearch8 import Elasticsearch
from pathlib import Path
import json
import hashlib
import os

# function taking document id as stting and returns hashed_id by md5
def create_document_hashed_id(id):
    m = hashlib.md5()
    id = id.encode('utf-8')
    m.update(id)
    hashed_id = str(int(m.hexdigest(), 16))[0:12]
    return hashed_id

# creates client for elasticsearch
_es = Elasticsearch(os.getenv('BTCTRANSCRIPTS_SERVER_URI'), basic_auth=(os.getenv('BTCTRANSCRIPTS_USER'),os.getenv('BTCTRANSCRIPTS_PASSWORD')))

# iterates over *.json files in processed_files directory and adds them to index
files = Path('../data/processed_files').glob('*.json')
for file in files:
    transcript_json = json.load(open(file))
    transcript_id = create_document_hashed_id(transcript_json['title']+' '+transcript_json['language'])

    #resp = _es.index(index='btctranscripts', doc_type="_doc", id=transcript_id, body=json.dumps(transcript_json))
    resp = _es.index(index='btctranscripts', id = transcript_id, document=transcript_json)

    print(resp['result'])





