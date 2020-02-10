import sqlite3

db = "tweet-data.db"

# Connect to sqlite3 DB
conn = sqlite3.connect(db)
c = conn.cursor()

# Delete Tables
cmds = ["DROP TABLE lang_data",
        "DROP TABLE trend_data",
        "DROP TABLE twt_data",
        "DROP TABLE country_data",
        "DROP TABLE love_data",
        "DROP TABLE pro_lang_data",
        "DROP TABLE hashtags_data",
        "DROP TABLE topics_data"
        ]
for cmd in cmds:
    try:
        c.execute(cmd)
    except:
        pass

# Create Tables
cmds = ["CREATE TABLE lang_data (language TEXT, top_lang TEXT, datetime TEXT)",
        "CREATE TABLE trend_data (trend TEXT, trend_id1 TEXT, trend_id2 TEXT, trend_id3 TEXT, datetime TEXT)",
        "CREATE TABLE twt_data (top_tweet TEXT, datetime TEXT)",
        "CREATE TABLE country_data (country TEXT, datetime TEXT)",
        "CREATE TABLE love_data (love_words INT, swear_words INT, datetime TEXT)",
        "CREATE TABLE pro_lang_data (pro_lang TEXT, datetime TEXT)",
        "CREATE TABLE hashtags_data (hashtag TEXT, datetime TEXT)",
        "CREATE TABLE topics_data (topic TEXT, datetime TEXT)"
        ]

# Execute all the commands
for cmd in cmds:
    c.execute(cmd)

# Commit the results and close the connection
conn.commit()
conn.close()
