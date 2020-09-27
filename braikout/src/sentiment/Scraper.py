import re

import tweepy
from textblob import TextBlob
from tweepy import OAuthHandler


class Scraper:
    def __init__(self):
        self.ckey = ""
        self.csecret = ""
        self.atoken = ""
        self.asecret = ""

        self.auth = OAuthHandler(self.ckey, self.csecret)
        self.auth.set_access_token(self.atoken, self.asecret)
        self.api = tweepy.API(self.auth)

    def clean_tweet(self, tweet):
        """
        clean tweets

        :param tweet: Tweet to analyze
        :type tweet str

        :return: Cleaned tweet
        :rtype: str
        """
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        """
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method

        :param tweet: Tweet to analyze
        :type tweet: str

        :return: Sentiment
        :rtype: str
        """

        analysis = TextBlob(self.clean_tweet(tweet))
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

    def get_tweets(self, query, count):
        """
        Main function to fetch tweets and parse them.

        :param query: Query for twitter API
        :type query: str

        :param count: Number of tweets to search
        :type count: int

        :return: tweets
        :rtype: List
        """
        tweets = []
        try:
            tweet_nums = self.api.search(q=query, count=count)
            for tweet in tweet_nums:
                cleaned_tweet = {'text': tweet.text, 'sentiment': self.get_tweet_sentiment(tweet.text)}
                if tweet.retweet_count > 0:
                    if cleaned_tweet not in tweets:
                        tweets.append(cleaned_tweet)
                else:
                    tweets.append(cleaned_tweet)
            return tweets

        except tweepy.TweepError as e:
            print("Error : " + str(e))

    def analyze_tweets_numerical(self, search_term):
        """
        return numbers for tweet analysis

        :param search_term: Term to analyze
        :type search_term: str

        :return: List of % for tweet sentiment categories
        :rtype: List
        """
        tweets = self.get_tweets(query=search_term, count=100000)
        eptweets = [tweet for tweet in tweets if tweet['sentiment'] == "Extremely positive"]
        vptweets = [tweet for tweet in tweets if tweet['sentiment'] == "Very positive"]
        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == "Positive"]
        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == "Neutral"]
        negtweets = [tweet for tweet in tweets if tweet['sentiment'] == "Negative"]

        return [self._perecentage_helper(tweets, x) for x in [eptweets, vptweets, ptweets, ntweets, negtweets]]

    def _perecentage_helper(self, tweets, subset):
        return 100 * (len(subset) / len(tweets))
