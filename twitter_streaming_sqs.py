import sys
import json
import tweepy
import requests
import math
import time
import boto3
from elasticsearch import Elasticsearch
from dateutil import parser
from datetime import datetime
from config import consumer_key, consumer_secret, access_token, access_secret, es_endpoint, google_api, AWS_Access_Key, AWS_Secret_Key
import urllib3
urllib3.disable_warnings()

if sys.version_info[0] == 2:
    from httplib import IncompleteRead
else:
    from http.client import IncompleteRead


FILTERED_KEYWORDS = ['Trump', 'China', 'Amazon', 'Football', 'War', 'Google', 'Love', 'Facebook', 'Movie', 'Music']

sqs_client = boto3.client(
                 "sqs",
                 aws_access_key_id=AWS_Access_Key,
                 aws_secret_access_key=AWS_Secret_Key,
                 region_name="us-east-1"
             )

sqs_queue = sqs_client.create_queue(QueueName="twitttrends")


class TweetStreamListener(tweepy.StreamListener):
    def __init__(self, es):
        self.es = es
        self.rate = 0
        self.other = 0

    def on_data(self, data):
            try:
                cur_data = json.loads(data)
                location = cur_data['user']['location']
                if location:
                    text = cur_data['text']
                    keyword = getKeyWord(text)
                    api_key = google_api
                    coordinates = getCoordinates(api_key, location)
                    timestamp = parser.parse(cur_data['created_at'])
                    timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
                    author = cur_data['user']['screen_name']
                    if (keyword and coordinates):
                        coordinates = '%s,%s' % (str(coordinates[0]), str(coordinates[1]))
                        mapping = {
                            'keyword': {
                                'StringValue': keyword,
                                'DataType': 'String'
                            },
                            'author': {
                                'StringValue': author,
                                'DataType': 'String'
                            },
                            'text': {
                                'StringValue': text,
                                'DataType': 'String'
                            },
                            'timestamp': {
                                'StringValue': timestamp,
                                'DataType': 'String'
                            },
                            'coordinates': {
                                'StringValue': coordinates,
                                'DataType': 'String'
                            },
                            'sentiment': {
                                'StringValue': 'Null',
                                'DataType': 'String'
                            },
                        }
                        try:
                            response = sqs_client.send_message(QueueUrl=sqs_queue['QueueUrl'], MessageBody=text, MessageAttributes=mapping)
                            print ("SQS Success!")
                        except Exception as e:
                            print (e)
                            pass
                    else:
                        print ("Unstructured data! Pass!")
                else:
                    print ("No location information! Pass!")
            except Exception as e:
                print (e)

    def on_status(self, status):
        print ("Status: " + status.text)

    def on_error(self, status_code):
        print ('Error:', str(status_code))
        if status_code == 420:
            print ("Rate Limited!")
            sleepy = 60 * math.pow(2, self.rate)
            print (time.strftime("%Y%m%d_%H%M%S"))
            print ("A reconnection attempt will occur in " + \
            str(sleepy/60) + " minutes.")
            time.sleep(sleepy)
            self.rate += 1
        else:
            sleepy = 5 * math.pow(2, self.other)
            print (time.strftime("%Y%m%d_%H%M%S"))
            print ("A reconnection attempt will occur in " + \
            str(sleepy) + " seconds.")
            time.sleep(sleepy)
            self.other += 1
        return True

    def on_timeout(self):
        return True


def getCoordinates(api_key, location):
    api_key = api_key
    api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(location, api_key))
    api_response_dict = api_response.json()
    if api_response_dict['status'] == "OK":
        latitude = api_response_dict['results'][0]['geometry']['location']['lat']
        longitude = api_response_dict['results'][0]['geometry']['location']['lng']
        coordinates = [longitude, latitude]
    else:
        coordinates = None
    return coordinates


def getKeyWord(text):
    for keyword in FILTERED_KEYWORDS:
        if (keyword in text or keyword.lower() in text or keyword.upper() in text):
            keyword = keyword
            break
        else:
            keyword = None
    return keyword


def main():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    es = Elasticsearch(hosts=es_endpoint, port=443, use_ssl=True)
    tweetStreamListener = TweetStreamListener(es)
    
    while True:
        try:
            tweetStream = tweepy.Stream(auth=api.auth, listener=tweetStreamListener)
            tweetStream.filter(track=FILTERED_KEYWORDS)
        except IncompleteRead:
            # reconnect and keep trucking
            tweetStream.disconnect()
            continue
        except KeyboardInterrupt:
            # exit
            tweetStream.disconnect()
            break


if __name__ == '__main__':
    main()
