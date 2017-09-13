from elasticsearch import Elasticsearch
from config import es_endpoint

es = Elasticsearch(hosts=es_endpoint, port=443, use_ssl=True)


def push_to_elasticsearch(tweet):    
    mapping = {
        'keyword': tweet['keyword'],
        'author': tweet['author'],
        'text': tweet['text'],
        'timestamp': tweet['timestamp'],
        'coordinates': tweet['coordinates'],
        'sentiment': tweet['sentiment'],
    }
    
    try:
        res = es.index(index="twitttrends", doc_type='tweet', body=mapping)
        print ("Push Status: ", res['created'])
    except Exception as e:
        print (e)
        pass
        
    
    
