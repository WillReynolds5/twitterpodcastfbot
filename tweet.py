import tweepy

from twitter_config import *

# Authenticate with Twitter
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)


def tweet(dict):

    try:
        # Post the first tweet
        tweet = api.update_status(dict['title'])

        for thread_item in dict['body']:
            # Post the second tweet in reply to the first
            tweet = api.update_status(thread_item, in_reply_to_status_id=tweet.id)

        print('Tweet Successful')

    except Exception as e:
        print(e)
