import json
from elasticsearch import Elasticsearch
from config import es_endpoint
import urllib3
urllib3.disable_warnings()

es = Elasticsearch(hosts=es_endpoint, port=443, use_ssl=True)


def tweets_geo(coordinates):
    tweet_geo = json.dumps({
                    "query" : {
                        "bool" : {
                            "must" : {
                                "match_all" : {}
                            },
                            "filter" : {
                                "geo_distance" : {
                                    "distance" : "100km",
                                    "coordinates" : coordinates
                                }
                            }
                        }
                    }
                })

    try:
        tweets_res = es.search(index="twitttrends", doc_type='tweet', body=tweet_geo)
    except Exception as e:
        print (e)
        return [], [], [], []
    
    geo_res = []
    text_res = []
    user_res = []
    sentiment_res = []
    for hit in tweets_res['hits']['hits']:
        geo = hit['_source']['coordinates']
        text = hit['_source']['text']
        user = hit['_source']['author']
        sentiment = hit['_source']['sentiment']
        if geo:
            geo_ret = [geo[1], geo[0]]
            print ("Proximity Coordinates", geo_ret)
            geo_res.append(geo_ret)
            text_res.append(text)
            user_res.append(user)
            sentiment_res.append(sentiment)

    return geo_res, text_res, user_res, sentiment_res


def tweets_filter(keyword):
    tweet_filter = json.dumps({
                       "from" : 0, "size" : 500,
                       "query": {
                           "match": {
                               'keyword': keyword
                           }
                       },
                       "sort": [
                           {
                               "timestamp": {
                                   "order": "desc"
                               }
                           }
                       ]
                   })
    
    try:
        tweets_res = es.search(index="twitttrends", doc_type='tweet', body=tweet_filter)
    except Exception as e:
        print (e)
        return [], [], [], []
    
    location_res = []
    text_res = []
    user_res = []
    sentiment_res = []
    for hit in tweets_res['hits']['hits']:
        coordinates = hit['_source']['coordinates']
        text = hit['_source']['text']
        user = hit['_source']['author']
        sentiment = hit['_source']['sentiment']
        if coordinates:
            coordinates_ret = [coordinates[1], coordinates[0]]
            print ("Current Coordinate", coordinates_ret)
            location_res.append(coordinates_ret)
            text_res.append(text)
            user_res.append(user)
            sentiment_res.append(sentiment)

    return location_res, text_res, user_res, sentiment_res


if __name__ == "__main__":
    tweets_filter('Trump')
