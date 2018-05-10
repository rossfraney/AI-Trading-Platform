import re

import tweepy
from textblob import TextBlob
from tweepy import OAuthHandler

ckey = "0DfRtRYGc1PuHb3CrDakpG30Y"
csecret = "7TDvdmlOZmnEkOQsa6Cak2d2pC8g6SMLUecI6dh9TXsFsKg3T0"
atoken = "2255066646-vUbXE5luGs53l3vXafrkPMKLSjpwl6PU3y2IfPP"
asecret = "T3xA2EnoLLjCIOYZ7jFRVcILvoR1qJCzlr6rJiA2jcVZv"

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

api = tweepy.API(auth)


def clean_tweet(tweet):
    """ clean tweets """
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def get_tweet_sentiment(tweet):
    """ Utility function to classify sentiment of passed tweet
    using textblob's sentiment method """
    # create TextBlob object of passed tweet text
    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0.75:
        return 'Extremely positive'
    elif analysis.sentiment.polarity > 0.5:
        return 'Very positive'
    elif analysis.sentiment.polarity > 0.25:
        return 'Positive'
    elif analysis.sentiment.polarity > 0:
        return 'Neutral'
    elif analysis.sentiment.polarity == 0:
        return 'Neutral'
    else:
        return 'Negative'


def get_tweets(query, count):
    """ Main function to fetch tweets and parse them. """
    # empty list to store parsed tweets
    tweets = []

    try:
        tweet_nums = api.search(q=query, count=count)
        for tweet in tweet_nums:
            cleaned_tweet = {'text': tweet.text, 'sentiment': get_tweet_sentiment(tweet.text)}
            if tweet.retweet_count > 0:
                if cleaned_tweet not in tweets:
                    tweets.append(cleaned_tweet)
            else:
                tweets.append(cleaned_tweet)
        return tweets

    except tweepy.TweepError as e:
        # print error (if any)
        print("Error : " + str(e))


def analyze_tweets_numerical(search_term):
    """ return numbers for tweet analysis """
    tweets = get_tweets(query=search_term, count=100000)
    eptweets = [tweet for tweet in tweets if tweet['sentiment'] == "Extremely positive"]
    vptweets = [tweet for tweet in tweets if tweet['sentiment'] == "Very positive"]
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == "Positive"]
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == "Neutral"]
    negtweets = [tweet for tweet in tweets if tweet['sentiment'] == "Negative"]

    # picking positive tweets from tweets
    epositive = (100 * len(eptweets) / len(tweets))
    vpositive = (100 * len(vptweets) / len(tweets))
    positive = (100 * len(ptweets) / len(tweets))
    neutral = (100 * len(ntweets) / len(tweets))
    negative = (100 * len(negtweets) / len(tweets))

    return [epositive, vpositive, positive, neutral, negative]
