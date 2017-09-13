import boto3
import requests
from config import AWS_Access_Key, AWS_Secret_Key, topic_arn

sns_client = boto3.client(
    "sns",
    aws_access_key_id=AWS_Access_Key,
    aws_secret_access_key=AWS_Secret_Key,
    region_name="us-east-1"
)


def retrieve_public_DNS():
    response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4')
    public_ip = response.text
    public_ip = public_ip.replace('.', '-')
    public_dns = "ec2-" + public_ip + ".compute-1.amazonaws.com"
    return public_dns


def subscribe_to_topic():
    public_dns = retrieve_public_DNS()
    #endpoint = "http://" + public_dns + ":5000/sns"
    endpoint = "http://" + public_dns + "/sns"
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='http',
            Endpoint=endpoint
        )
        print ("Send Subscription Request...")
    except Exception as e:
        print (e)

