# TwittTrends
## COMSW6998 Clouding Computing and Big Data
## Assignment 2: TwittMap with Trends and Sentiment Analysis
<br>HW Group 30 <br>
Authors: <br>
Kuang Yang, ky2342 <br>
Xun Xue, xx2241

### Architecture Diagram:
http://i.imgur.com/ouIDUJT.png

### Step 1: Create Amazon Elasticsearch Service domain
* We choose **Elasticsearch** version 2.3. The instance type is t2.micro. The storage type is EBS.
* Select the access policy to allow open access to the domain for simplicity. You should choose a stricter policy in the real-world application.

### Step 2: Create Index on AWS Elasticsearch
* Run the command below in the terminal(This command is stored in the file *ES_Initialization/create_initial_index.txt*). In the endpoint of domain *twitttrends*, it creates an index(database) called *twitttrends* with its type as *tweet*.
```
curl -XPUT search-twitttrends-kojvsfuimmqmy6aqimmrz3smbi.us-east-1.es.amazonaws.com/twitttrends -d '
{
    "mappings": {
        "tweet": {
            "properties": {
                "keyword": {
                    "type": "string"
                },
                "author": {
                    "type": "string"
                },
                "text": {
                    "type": "string"
                },
                "timestamp": {
                    "type": "date"
                },
                "coordinates": {
                    "type": "geo_point"
                },
                "sentiment": {
                    "type": "string"
                }
            }
        }
    }
}'
```

### Step 3: Set up AWS SQS (and Apache Kafka) as the Queue (Bonus Part)
* Install **Apache Kafka** on your machine. See Kafka Quickstart: http://kafka.apache.org/quickstart
* See files under directory *Kafka_Setup/*. *Kafka_Commandlines.txt* contains some useful commandlines in **Kafka**. Please run `sh kafkastart.sh` first to start Kafka server. Run `sh kafkastopt.sh` to stop kafka server.
* Here I also use **AWS SQS** as the queue.

### Step 4: Collect Tweets Streaming into Kafka Queue (and AWS SQS)
* Run `pip install -r requirements.txt` first to install dependencies.
* To collect tweets into the queue, please run `python twitter_streaming_kafka.py` using **Kafka** or `python twitter_streaming_sqs.py` using **AWS SQS**.
* This program uses **Twitter Streaming API** and **Tweepy** to fetch real-time tweets from the twitter hose into **Kafka queue** or **AWS SQS**.
* Link to Tweepy: https://github.com/tweepy/tweepy
* Comments: This application is able to run under both Python2 and Python3 environment with correct syntaxes of all codes. **However, Python2 is more preferred**. I guarantee that all codes can run under **Python2.7**. I might forget to add parentheses after some print statements. So this application may not run successsfully under Python3 due to this minor issue. If you encountered any issues, make sure you test under Python2 environment. If you have any problems in collecting tweets streaming, update your Tweepy first and restart this script manually. Thanks!

### Step 5: Define a Worker Pool to Consume Tweets from Kafka (and AWS SQS) and Perform Sentiment Analysis
* To consume tweets from the queue, please run `python twitter_consumer_kafka.py` using **Kafka** or `python twitter_consumer_sqs.py` using **AWS SQS**.
* These workers should each run on a separate pool thread.
* Consume tweets out of **Kafka queue** or **AWS SQS** and then perform sentiment analysis on each tweet using **IBM Natural Language Understanding**. This can return a positive, negative or neutral sentiment evaluation for the text of the submitted Tweet.

### Step 6: Send Tweets to AWS Simple Notification Service (SNS)
* As soon as the tweet is processed, publish the tweet to a topic in **AWS SNS**. **AWS SNS** will send a message containing all information about this tweet to an HTTP endpoint (at backend side) which has subscribed this topic.

### Step 7: Store Tweets
* On receiving the message, in the backend, index this tweet in **AWS Elasticsearch**. Make sure you preserve the sentiment of the tweet as well.

### Step 8: Create Web UI
* Create a Web UI using **HTML** and **JavaScript** to allow users to choose any keyword(up to 10) through a dropdown box.
* Initialize **Google Map** using **Google Maps API**.
* Create "**Start Live Streaming**" and "**Stop Live Streaming**" buttons which are used to enable and disable showing live twitter streaming on the map.

### Step 9: Filter Tweets
* Use **Python** **Flask** framework as the backend server connected to **AWS Elasticsearch**.
* Use **jQuery** and **AJAX** to communicate between the frontend and backend.
* Query tweets data on **AWS Elasticsearch** according to the keyword selected by the user in the frontend.
* Use **Flask Socket** to dynamically display real-time tweets on the map.
* Bonus Part: Filter tweets using ElasticSearch’s geospatial feature that shows tweets that are within a certain distance from the point the user clicks on the map.

### Step 9: Visualize Filtered Tweets and Display Live Twitter Streaming
* For keyword and live streaming filter, I use markers with different colors (**green: positive, yellow: neutral, purple: negaive**) to plot tweets with different sentiments.
* To start show real-time tweets on the map, please click the green button "**Start Live Streaming**".
* To stop show real-time tweets on the map, please click the green button "**Stop Live Streaming**".
* Please click "**Refresh**" button to clear all markers out of the map.
* For the point which the user clicks on the map, I attach a flag on it every time, and when you click on it, it will pop out an infowindow to show its coordinates. For gepspatial feature filter, I add a listener event to each marker. Whenever the user clicks the marker, an infowindow is popped out to show the contents of the tweet, its author and its sentiment.

### Step 7: Deploy the Web App on AWS Elastic Beanstalk
* To deploy **Python Flask** web app on **AWS Elastic Beanstalk**, see documents here: http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
* Here I use **Python2.7** environment. Also, when you zip your project, please remember that first `cd` into the root directory of your project and then zip all codes and file. Don't zip them in the same level of your project folder.

### Link to My TwittTrends Web App:
* http://twitttrends-group30.xbsfi2zcmp.us-east-1.elasticbeanstalk.com/

### Issues about Deloyment:
* There are two major components (the worker and the web application) in this whole project. See the diagram above.
* The "worker" (collects data streaming, consumes **Kafka** queue, processes data and sends to **AWS SNS**) can be deployed on the local machine or **AWS EC2**.
* The web application can be deployed on **AWS EC2** or **AWS Elastic BeanStalk**.
* If the web application was deployed on **AWS EC2**: <br>
  (1) If you configure your server using **Nginx** and **Gunicorn**, please see two links here: <br>
  https://www.matthealy.com.au/blog/post/deploying-flask-to-amazon-web-services-ec2/ <br>
  http://cheng.logdown.com/posts/2015/04/17/better-way-to-run <br>
  (2) If you configure your server with the original method (**python application** and run on IP/PublicDNS:5000), please see the link here: <br>
  http://stackoverflow.com/questions/32118574/flask-application-on-amazon-ec2 <br>
  Regarding **AWS Elastic Beanstalk**, please see Step 7.
