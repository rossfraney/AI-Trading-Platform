import json

from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
# TODO FIX


class listener(StreamListener):

    ckey = ""
    csecret = ""
    atoken = ""
    asecret = ""

    def on_data(self, data):
        all_data = json.loads(data)

        tweet = all_data["text"]
        sentiment_value, confidence = s.sentiment(tweet)

        if confidence*100 >= 80:
            output = open("twitter-out.txt", "a")
            output.write(sentiment_value)
            output.write('\n')
            output.close()

        return True

    def on_error(self, status):
        raise Exception(status)


auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["happy"])
