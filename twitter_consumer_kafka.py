import json
import boto3
from kafka import KafkaConsumer
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from twitter_streaming_kafka import KAFKA_TOPIC, KAFKA_PORT
from sentiment_analysis import getSentiment
from config import AWS_Access_Key, AWS_Secret_Key, topic_arn

consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_PORT)

sns_client = boto3.client(
    "sns",
    aws_access_key_id=AWS_Access_Key,
    aws_secret_access_key=AWS_Secret_Key,
    region_name="us-east-1"
)


def twitter_analysis():
    for message in consumer:
        tweet = json.loads(message.value.decode('utf-8'))
        tweet['sentiment'] = getSentiment(tweet['text'])
        if tweet['sentiment']:
            tweet = json.dumps(tweet)
            print (tweet)
            try:
                response = sns_client.publish(TopicArn=topic_arn, Message=json.dumps({'default': tweet}), MessageStructure='json')
                print (response)
            except Exception as e:
                print (e)
        else:
            print "No Sentiment Result! Pass!"


def main():
    executor = ThreadPoolExecutor(max_workers=4)
    while True:
        executor.submit(twitter_analysis)
        sleep(1)


if __name__ == '__main__':
    main()
