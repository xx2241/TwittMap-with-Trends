import os
import sys
import random
import watson_developer_cloud
import watson_developer_cloud.natural_language_understanding.features.v1 as features
from config import IBM_nlu_username, IBM_nlu_password


def getSentiment(text):
    nlu = watson_developer_cloud.NaturalLanguageUnderstandingV1(version='2017-02-27', username=IBM_nlu_username, password=IBM_nlu_password)
    try:
        sentiment =  nlu.analyze(text=text, features=[features.Sentiment()])
        sentiment = sentiment['sentiment']['document']['label']
    except Exception as e:
        print (e)
        print "Select the sentiment randomly!"
        sentiment_list = ['positive', 'neutral', 'negative']
        random_selection = random.randrange(3)
        sentiment = sentiment_list[random_selection]
        
    return sentiment


if __name__ == "__main__":
    text = "This is a dog."
    getSentiment(text)
