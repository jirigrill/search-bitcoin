"""
uploads json to elastic
"""
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



def upload_to_elastic(transcript_json):
    """
    Creates elasticsearch client and uploads transcript_json there
    """
    # creates client for elasticsearch
    _es = Elasticsearch(os.getenv('BTCTRANSCRIPTS_SERVER_URI'), basic_auth=(os.getenv('BTCTRANSCRIPTS_USERNAME2'),os.getenv('BTCTRANSCRIPTS_PASSWORD')))

    TRANSCRIPT_ID = create_document_hashed_id(transcript_json['title']+' '+transcript_json['language'])

    resp = _es.index(index='btctranscripts', id = TRANSCRIPT_ID, document=transcript_json)
    print(f"elastic response: {resp['result']}")
    return resp['result']

