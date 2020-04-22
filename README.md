# tweet news rank - Identifying and grading news using social media factors

This is a twitter data analyser in real time. It gets twitter data using Twitter API, analyses it, categorize the news and  create graphs based on the generated data and rank the most popular topic that is being discussed on twitter.

### Steps to run the Project

1. ##### Install the required modules

    ```pip3 install -r requirements.txt```

2. ##### Key generation

    To run this project you need twitter access key, access secret, consumer key and consumer secret, You can generate these by raising a request for twitter developer account at http://dev.twitter.com/.

3. ##### Update Keys in Project

    After generating the keys place them inside local_config.py file.

4. ##### Get Twitter data

    ```python3 create-db.py```
    ```python3 tweet.py```
    > This will take some time depending on number of tweets configured in tweet.py

5. ##### Run Flask Web App

    ```python3 app.py```
    > Open http://localhost:5000/ to see the twitter data analysis.
