#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, make_response
import sqlite3
import ast

db = "data/tweet-data.db"

app = Flask(__name__)


@app.route("/")
def main():
    login = request.cookies.get('login')
    if (login != 'success'):
        return redirect("/login")
    lang_data = []
    top_lang_data = []
    country_data = []
    love_words = []
    love_words_guage = []
    pro_lang_data = []
    hashtag_data = []
    topics_data = []
    lang, top_lang, country, lv_words, sw_words, pro_lang, hashtag, topics, datetime_twt = get_data_from_db()

    # Form Lang Data
    for l in lang:
        # 1st--language, 2nd--percentage used, 3rd--same thing repeated
        lang_data.append([l[0], l[1], l[1]])

    # Form Top Lang Data
    for tl in top_lang:
        top_lang_data.append([tl[0], tl[1], tl[1]])

    # Form Country Data
    country_data.append(['Country', 'Popularity'])
    for ct in country:
        country_data.append([ct[0], ct[1]])

    # Form Love Words and Swear Words
    love_words.append(['love_words', lv_words, lv_words])
    love_words.append(['swear_words', sw_words, sw_words])
    lw_percents = int((lv_words * 100) / (lv_words + sw_words))
    sw_percents = int((sw_words * 100) / (lv_words + sw_words))
    love_words_guage.append(['Labels', 'Value'])
    love_words_guage.append(['love_words', lw_percents])
    love_words_guage.append(['swear_words', sw_percents])

    # Form Programming Languages Data
    for p in pro_lang:
        pro_lang_data.append([p[0], p[1], p[1]])

    # Form HashTags Data
    others = 0
    for h in hashtag:
        if h[1] > 5:
            hashtag_data.append([h[0], h[1], h[1]])
        else:
            others += h[1]
    # hashtag_data.append(['others', others, others])

    # Sort the topics based on occurrence
    topics = sorted(topics, key=lambda x: x[1])

    # Form Topics Data
    for t in topics:
        topics_data.append([t[0], t[1], t[1]])

    # Most Trending Topic
    trending_topic = ("india", 0)
    for t in topics:
        if t[1] > trending_topic[1]:
            trending_topic = t

    return render_template("analyser.html", lang_data=lang_data, top_lang_data=top_lang_data,
                           country_data=country_data, love_words=love_words, trending_topic=trending_topic,
                           love_words_guage=love_words_guage, datetime_twt=datetime_twt,
                           pro_lang_data=pro_lang_data, hashtag_data=hashtag_data, topics_data=topics_data)


def get_data_from_db():
    # Connect to sqlite DB
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cn = conn.cursor()

    # Get Language Data from DB
    cn.execute("SELECT * FROM lang_data ORDER BY datetime DESC LIMIT 1")
    result = cn.fetchone()
    lang_data = ast.literal_eval(result['language'])
    top_lang_data = ast.literal_eval(result['top_lang'])

    # Get Countries Data from DB
    cn.execute("SELECT * FROM country_data ORDER BY datetime DESC LIMIT 1")
    result = cn.fetchone()
    country_data = ast.literal_eval(result['country'])

    # Get Love and Swear words Data from DB
    cn.execute("SELECT * FROM love_data ORDER BY datetime DESC LIMIT 1")
    result = cn.fetchone()
    love_words_data = result['love_words']
    swear_words_data = result['swear_words']

    # Get Programming Languages Data from DB
    cn.execute("SELECT * FROM pro_lang_data ORDER BY datetime DESC LIMIT 1")
    result = cn.fetchone()
    pro_lang_data = ast.literal_eval(result['pro_lang'])

    # Get HashTags Data from DB
    cn.execute("SELECT * FROM hashtags_data ORDER BY datetime DESC LIMIT 1")
    result = cn.fetchone()
    hashtags_data = ast.literal_eval(result["hashtag"])
    # hashtags_data_str = []
    # for i, j in hashtags_data:
    #     hashtags_data_str.append((str(i.encode('utf-8')), j))
    # print(hashtags_data_str)

    # Get Topics Data from DB
    cn.execute("SELECT * FROM topics_data ORDER BY datetime DESC LIMIT 1")
    result = cn.fetchone()
    topics_data = ast.literal_eval(result['topic'])

    # Get time of insertion into DB
    datetime_twt = result['datetime']

    conn.close()

    return lang_data, top_lang_data, country_data, love_words_data, swear_words_data, \
           pro_lang_data, hashtags_data, topics_data, datetime_twt


@app.route("/top_tweets")
def top_tweets():
    tweets, datetime_top_tweets = get_top_tweet()
    # datetime_top_tweets is only for debug, just so that we can check the script is running regularly
    return render_template("top_tweets.html", tweets=tweets, datetime_top_tweets=datetime_top_tweets)


def get_top_tweet():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cn = conn.cursor()
    cn.execute("SELECT * FROM twt_data ORDER BY datetime DESC LIMIT 30")  # Get last 30 tweets

    result = cn.fetchall()
    tweets = []
    datetime_top_tweets = result[0]['datetime']

    for tweet in result:
        tweets.append(tweet['top_tweet'])

    conn.close()
    return tweets, datetime_top_tweets


@app.route("/trends")
def trends():
    trend, trend_tweets, datetime_trends = get_trends()
    return render_template("trends.html", trend=trend, trend_tweets=trend_tweets, datetime_trends=datetime_trends)


def get_trends():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cn = conn.cursor()
    cn.execute("SELECT * FROM trend_data ORDER BY datetime DESC LIMIT 10")  # return top 10 trends

    trend = []
    trend_tweets = []

    result = cn.fetchall()
    datetime_trends = result[0]['datetime']

    for tt in result:
        trend.append(tt['trend'])
        trend_tweets.append(tt['trend_id1'])
        trend_tweets.append(tt['trend_id2'])
        trend_tweets.append(tt['trend_id3'])

    conn.close()
    return trend, trend_tweets, datetime_trends


@app.route('/login', methods=["POST", "GET"])
def login():
    login = request.cookies.get('login')
    if (login == 'success'):
        return redirect("/")
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin@123':
            resp = make_response(render_template("login.html", status='success'))
            resp.set_cookie("login", "success")
            resp.body = "success"
            return resp
        else:
            resp = make_response(render_template('login.html', status='failure'))
            return resp
    return render_template('login.html', status='none')


@app.route("/logout")
def logout():
    resp = make_response(render_template("login.html", status="logout"))
    resp.delete_cookie('login')
    return resp


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
