#!/usr/bin/env python3

import tweepy
from local_config import *
from tweepy import Stream
from tweepy.streaming import StreamListener
import json
from collections import Counter
import sqlite3
import time
import ml_model
import re


class TwtUtils():
    def __init__(self, api):
        self.api = api

    def get_tweet_html(self, id):
        oembed = self.api.get_oembed(id=id, hide_media=True, hide_thread=True)
        twt_html = oembed['html'].strip('\n')
        return twt_html


class Stats():
    def __init__(self):
        self.lang = []
        self.top_lang = []
        self.top_tweets = []
        self.countries = []
        self.tweets_grab = 0
        self.love_words = 0
        self.swear_words = 0
        self.programing_lang = []
        self.hashtags = []
        self.topics = []

    def add_lang(self, lang):
        self.lang.append(lang)

    def add_top_lang(self, top_lang):
        self.top_lang.append(top_lang)

    def add_top_tweets(self, tweet_html):
        self.top_tweets.append(tweet_html)

    def add_countries(self, country):
        self.countries.append(country)

    def add_hashtags(self, hashtags):
        for hashtag in hashtags:
            self.hashtags.append(hashtag['text'])

    def set_tweets_grab(self):
        self.tweets_grab += 1

    def get_tweets_grab(self):
        return self.tweets_grab

    def found_love_words(self):
        self.love_words += 1

    def found_swear_words(self):
        self.swear_words += 1

    def add_programing_lang(self, pro_lang):
        self.programing_lang.append(pro_lang)

    def add_news_topic(self, topic):
        self.topics.append(topic)

    def get_stats(self):
        return self.lang, self.top_lang, self.top_tweets, self.countries, self.love_words, self.swear_words, \
               self.programing_lang, self.hashtags, self.topics


# Twitter Stream Listener Class
class TwitterListener(StreamListener):
    def __init__(self, num_tweets_to_grab, stats, twt_utils, retweet_count):
        super().__init__()
        self.num_tweets_to_grab = num_tweets_to_grab
        self.stats = stats
        self.twt_utils = twt_utils
        self.retweet_count = retweet_count
        self.tweets_grab = 0

    def on_data(self, data):
        json_data = []
        try:
            json_data = json.loads(data)
            try:
                if (json_data['lang'] != 'en'):
                    return True
                self.stats.add_lang(langs[json_data['lang']])
                retweet_count = json_data['retweeted_status']['retweet_count']

                if retweet_count >= self.retweet_count:
                    self.stats.add_top_lang(langs[json_data['lang']])
                    twt_html = self.twt_utils.get_tweet_html(json_data['id'])
                    self.stats.add_top_tweets(twt_html)
            except:
                pass;

            tweet = json_data['text']

            # predict the news category
            topic = ml_model.predict(tweet)
            self.stats.add_news_topic(topic)

            # extract hashtags
            self.stats.add_hashtags(json_data["entities"]["hashtags"])

            # try catch here to avoid multiple repeat error for regex
            try:
                for country in countries_list:
                    country_local = "\\b" + country + "\\b"
                    if re.findall(country_local, tweet, flags=re.IGNORECASE):
                        self.stats.add_countries(country)

                # This is for USA & UK, since no one uses its full name on Twitter
                if re.findall("\\busa\\b", tweet, flags=re.IGNORECASE):
                    self.stats.add_countries("United States")

                if re.findall("\\bbritain\\b", tweet, flags=re.IGNORECASE):
                    self.stats.add_countries("United Kingdom")

                for lw in love_words:
                    if lw in tweet.lower():
                        self.stats.found_love_words()

                for lw in swear_words:
                    if lw in tweet.lower():
                        self.stats.found_swear_words()

                for pro_lang in programing_lang_list:
                    pro_lang_local = "\\b" + pro_lang + "\\b"
                    if re.findall(pro_lang_local, tweet, flags=re.IGNORECASE):
                        self.stats.add_programing_lang(pro_lang)
            except:
                pass

            self.stats.set_tweets_grab()
            twts_grabbed = self.stats.get_tweets_grab()
            print("\rTweets Grabbed = ", twts_grabbed, end="")
            if twts_grabbed >= self.num_tweets_to_grab:
                return False

            return True

        except Exception as e:
            if e.args != ('text',):
                print("\nError occurred while parsing a tweet")
                print(json_data)
                print(e)

    def on_error(self, status):
        print("\nError occurred while streaming a tweet!")
        print(status)
        if status == 420:
            time.sleep(300)  # Sleep for 5 minutes


# Main function, all main works here
class TwitterMain():
    def __init__(self, num_tweets_to_grab, retweet_count, conn):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

        self.api = tweepy.API(self.auth)
        self.twt_utils = TwtUtils(self.api)

        self.stats = Stats()

        self.conn = conn
        self.c = self.conn.cursor()

        self.num_tweets_to_grab = num_tweets_to_grab
        self.retweet_count = retweet_count

    # Stremning data
    def get_streaming_data(self):
        print("Twitter Streaming started..")
        twts_grabbed = 0
        while twts_grabbed < self.num_tweets_to_grab:

            twitter_stream = Stream(self.auth, TwitterListener(self.num_tweets_to_grab - twts_grabbed, self.stats,
                                                               self.twt_utils, self.retweet_count), tweet_mode="extended")
            try:
                # filter only indian languages
                twitter_stream.filter(track=tracks, languages=indian_langauges)
                # twitter_stream.sample()
            except Exception as e:
                print("\nError while Streaming.")
                print(e)
                print("Sleeping for 30 seconds")
                time.sleep(30)  # Sleep for 5 minutes if error occurred
                print("Resuming Stream...")
            finally:
                twts_grabbed = self.stats.get_tweets_grab()
        print("\nTwitter Streaming is done..")

        lang, top_lang, top_tweets, countries, love_words_data, swear_words_data, pro_lang, hashtags, topics = self.stats.get_stats()

        print("Inserting the Twitter Stream Data to DB..")

        # Inserting lang data and top lang data to DB
        lang_data = str(list(Counter(lang).items()))
        top_lang_data = str(list(Counter(top_lang).items()))
        self.c.execute("INSERT INTO lang_data VALUES (?,?, DATETIME('now'))",
                       (lang_data, top_lang_data))
        print("Lang Data = ", lang_data)
        print("Top Lang Data = ", top_lang_data)

        # Add top tweets to DB
        for tt in top_tweets:
            self.c.execute("INSERT INTO twt_data VALUES (?, DATETIME('now'))", (tt,))

        # Add Love Words and Swear Words to DB
        self.c.execute("INSERT INTO love_data VALUES (?,?, DATETIME('now'))", (love_words_data, swear_words_data))
        print("Love Words = {}\nSwear Words = {}".format(love_words_data, swear_words_data))

        # Add Countries data to DB
        countries_data = str(list(Counter(countries).items()))
        self.c.execute("INSERT INTO country_data VALUES (?, DATETIME('now'))", (countries_data,))
        print("Countries Data = ", countries_data)

        # Add Programming Languages to DB
        programming_languages_data = str(list(Counter(pro_lang).items()))
        self.c.execute("INSERT INTO pro_lang_data VALUES (?, DATETIME('now'))", (programming_languages_data,))
        print("Programming Languages Data = ", programming_languages_data)

        # Add hashtags to DB
        hashtags_data = str(list(Counter(hashtags).items()))
        self.c.execute("INSERT INTO hashtags_data VALUES (?, DATETIME('now'))", (hashtags_data,))
        print("HashTags Data = ", hashtags_data)

        # Add topic data to DB
        topics_data = str(list(Counter(topics).items()))
        self.c.execute("INSERT INTO topics_data VALUES (?, DATETIME('now'))", (topics_data,))
        print("Topics Data = ", topics_data)

        self.conn.commit()
        print("Insertion to DB is done..")

    # end streaming

    # Grab trends from twitter
    def get_trends(self):
        print("Trends Streaming Started..")
        trends = self.api.trends_place(1)
        trend_data = []
        print("Got Trends place")

        for trend in trends[0]["trends"]:
            trend_tweets = []
            # print trend['name']
            trend_tweets.append(trend['name'])

            search_results = tweepy.Cursor(self.api.search, q=trend['name']).items(3)
            for result in search_results:
                twt_html = self.twt_utils.get_tweet_html(result.id)
                trend_tweets.append(twt_html)
                # print twt_html

            trend_data.append(tuple(trend_tweets))

        self.c.executemany("INSERT INTO trend_data VALUES (?, ?, ?, ?, DATETIME('now'))", trend_data)
        self.conn.commit()

    # End trends


if __name__ == "__main__":
    num_tweets_to_grab = 20000
    retweet_count = 1000
    conn = None
    try:
        conn = sqlite3.connect(db)
        twt = TwitterMain(num_tweets_to_grab, retweet_count, conn)
        twt.get_streaming_data()
        time.sleep(30)
        twt.get_trends()

    except Exception as e:
        print(e)

    finally:
        if conn:
            conn.close()
