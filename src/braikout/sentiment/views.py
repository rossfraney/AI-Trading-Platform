from django.shortcuts import render

# Create your views here.
import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import matplotlib.pyplot as plt

def calctime(a):
    return time.time() - a

positive = 0
negative = 0
compound = 0

count = 0
initime = time.time()
plt.ion()

ckey = "0DfRtRYGc1PuHb3CrDakpG30Y"
csecret = "7TDvdmlOZmnEkOQsa6Cak2d2pC8g6SMLUecI6dh9TXsFsKg3T0"
atoken = "2255066646-vUbXE5luGs53l3vXafrkPMKLSjpwl6PU3y2IfPP"
asecret = "T3xA2EnoLLjCIOYZ7jFRVcILvoR1qJCzlr6rJiA2jcVZv"


class listener(StreamListener):

    def on_data(self, data):

        all_data = json.loads(data)

        tweet = all_data["text"]
        sentiment_value, confidence = s.sentiment(tweet)
        print(tweet, sentiment_value, confidence)

        if confidence*100 >= 80:
            output = open("twitter-out.txt","a")
            output.write(sentiment_value)
            output.write('\n')
            output.close()

        return True

    def on_error(self, status):
        print(status)


auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["happy"])
