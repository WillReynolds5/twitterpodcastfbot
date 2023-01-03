import tweepy

from twitter_config import *

# Authenticate with Twitter
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)


def tweet():
    # Post the first tweet
    tweet1 = api.update_status('Hello, world!')

    # Post the second tweet in reply to the first
    tweet2 = api.update_status('This is the second tweet in my thread.', in_reply_to_status_id=tweet1.id)
