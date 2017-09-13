import boto3
from flask import *
from twitter_filter import tweets_filter, tweets_geo
from push_to_es import push_to_elasticsearch
from subscriber import subscribe_to_topic
from flask.ext.socketio import SocketIO, emit
from threading import Thread, Event
from time import sleep
from config import AWS_Access_Key, AWS_Secret_Key

application = Flask(__name__)
socketio = SocketIO(application)
global subscribed
subscribed = False
global tweet
tweet = None
global oldtweet
oldtweet = None

sns_client = boto3.client(
                "sns",
                aws_access_key_id=AWS_Access_Key,
                aws_secret_access_key=AWS_Secret_Key,
                region_name="us-east-1"
            )

if subscribed == False:
    subscribe_to_topic()

thread = Thread()
thread_stop_event = Event()


class TweetThread(Thread):
    def __init__(self):
        self.delay = 1
        super(TweetThread, self).__init__()

    def tweetsender(self):
        while not thread_stop_event.isSet():
            global tweet
            global oldtweet
            if (tweet == oldtweet):
                print ("Waiting!")
                continue
            oldtweet = tweet
            if tweet == None:
                print ("Wait for tweet coming!")
                continue
            socketio.emit('livetweet', tweet, namespace='/live')
            print ("Server emits tweet...")
            sleep(self.delay)

    def run(self):
        self.tweetsender()


@application.route('/', methods=['GET', 'POST'])
def Initialize():
    global subscribed
    if subscribed == False:
        subscribe_to_topic()
    return render_template('TwittTrends.html')


@socketio.on('connect', namespace='/live')
def connect():
    global thread
    global thread_stop_event
    thread_stop_event = Event()
    print ("Socket Connected!")
    if not thread.isAlive():
        thread = TweetThread()
        thread.start()


@socketio.on('disconnect', namespace='/live')
def disconnect():
    thread_stop_event.set()
    print ("Socket Disconnected!")


@application.route('/sns', methods=['GET', 'POST'])
def getSNS():
    if request.method == 'POST':
        global subscribed
        if subscribed == False:
            subscribe_to_topic()
        data = json.loads(request.data.decode())
        if request.headers['X-Amz-Sns-Message-Type'] == 'SubscriptionConfirmation':
            print ("Start SNS Subscription Confirmation...")
            topicArn = data['TopicArn']
            token = data['Token']
            try:
                sns_client.confirm_subscription(TopicArn=topicArn, Token=token)
                subscribed = True
                print ("SNS Subscription Confirmed!")
            except Exception as (e):
                print (e)
        elif request.headers['X-Amz-Sns-Message-Type'] == 'Notification':
            print ("Get the Message...")
            global tweet
            tweet = json.loads(data['Message'])
            push_to_elasticsearch(tweet)
        return ''


@application.route('/keyword', methods=['GET', 'POST'])
def tweetmap():
    if request.method == 'POST':
        tags = request.form['tags']
        print("tags:", tags)
        locs, text, user, sentiment = tweets_filter(tags)
        print (locs)
        print (text)
        print (user)
        print (sentiment)
        return json.dumps({'locs': locs, 'text': text, 'user': user, 'sentiment': sentiment})
    else:
        return json.dumps({'locs': [], 'text': [], 'user': [], 'sentiment': []})


@application.route('/local', methods=['GET','POST'])
def tweetgeo():
    if request.method == 'GET':
        lat = float(request.args['lat'])
        lng = float(request.args['lng'])
        coordinates = [lng, lat]
        print ([coordinates[1], coordinates[0]])
        locs, text, user, sentiment = tweets_geo(coordinates)
        print (locs)
        print (text)
        print (user)
        print (sentiment)
        return jsonify({'locs': locs, 'text': text, 'user': user, 'sentiment': sentiment})
    else:
        return jsonify({'locs': [], 'text': [], 'user': [], 'sentiment': []})


if __name__ == "__main__":
    socketio.run(application, host='0.0.0.0', debug=True)

