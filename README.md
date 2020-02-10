# Identifying and grading news using social media factors

### This is a twiter data analyser. That analyse twitter data in real time. It gets twitter data using Twitter API, analyses it and create graphs based on that data and ranks the most popular topic being discussed on twitter

## Installation

    pip3 install -r requirements.txt


## Usage

##### Create a twitter developer account and Gets keys from `keys and access tokens` and put in local_config.py file.
#### then run this python files

    python3 create-db.py
    python3 tweet.py

>**tweet.py** will take some time to get results from twitter.

#### All data are saved now in database. Now we can run the web application.

    python3 app.py

#### Open localhost(:5000 or whatever the port) then see result.
