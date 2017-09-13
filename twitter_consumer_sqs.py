import json
import boto3
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from sentiment_analysis import getSentiment
from config import AWS_Access_Key, AWS_Secret_Key, topic_arn

sns_client = boto3.client(
                 "sns",
                 aws_access_key_id=AWS_Access_Key,
                 aws_secret_access_key=AWS_Secret_Key,
                 region_name="us-east-1"
             )

sqs_client = boto3.client(
                 "sqs",
                 aws_access_key_id=AWS_Access_Key,
                 aws_secret_access_key=AWS_Secret_Key,
                 region_name="us-east-1"
             )

sqs_queue = sqs_client.create_queue(QueueName="twitttrends")


def twitter_analysis():
    try:
        messages = sqs_client.receive_message(QueueUrl=sqs_queue['QueueUrl'], AttributeNames=['All'], MessageAttributeNames=['All'], MaxNumberOfMessages=2)
    except Exception as e:
        print (e)
    for message in messages['Messages']:
        tweet = {}

        keyword = message['MessageAttributes']['keyword']['StringValue']
        tweet['keyword'] = keyword

        user = message['MessageAttributes'].get('author').get('StringValue')
        tweet["author"] = user

        text = message['Body']
        tweet["text"] = text

        timestamp = message['MessageAttributes']['timestamp']['StringValue']
        tweet['timestamp'] = timestamp
        
        loc0 = float((((message['MessageAttributes'])['coordinates']['StringValue']).split(','))[0])
        loc1 = float((((message['MessageAttributes'])['coordinates']['StringValue']).split(','))[1])
        locs = [loc0, loc1]
        tweet["coordinates"] = locs
        
        sentiment = getSentiment(tweet['text'])
        tweet["sentiment"] = sentiment

        if sentiment:
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
