import re
from textblob import TextBlob
from flask import Flask, render_template, request

from newsdataapi import NewsDataApiClient

app = Flask(__name__)
app.static_folder = 'static'

api = NewsDataApiClient(apikey='pub_34428f75ef514735b92c05edc03f3cbd6c309')


app.config['negative_count'] = 0
app.config['positive_count'] = 0
app.config['neutral_count'] = 0


def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\\w+:\/\/\S+)", " ", tweet).split())



def get_tweet_polarity(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    return analysis.sentiment.polarity

def get_tweet_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity == 0:
        return "neutral"
    else:
        return "negative"

def get_tweets(api, query, count):
    tweets = []
    fetched_tweets = []
    api = NewsDataApiClient(apikey='pub_34428f75ef514735b92c05edc03f3cbd6c309')

    response = api.news_api(q=query, language='en', size=count)

    for article in response['results']:
        fetched_tweets.append({
            'title': article['title'],
            'date': article['pubDate'],  # Assuming 'pubDate' contains the publication date
            'source_name': article.get('source_id', 'Unknown'),  # Use 'source_id' as source name; default to 'Unknown' if not present
             'link': article['link'],  # Add the link attribute
        })

    for tweet in fetched_tweets:
        parsed_tweet = {}
        
        parsed_tweet['text'] = tweet['title']
        parsed_tweet['sentiment'] = get_tweet_sentiment(parsed_tweet['text'])
        parsed_tweet['date'] = tweet['date']
        parsed_tweet['source_name'] = tweet['source_name']
        parsed_tweet['link'] = tweet['link']
        parsed_tweet['polarity'] = get_tweet_polarity(tweet['title'])
        
        # Update sentiment counts based on sentiment
        if parsed_tweet['sentiment'] == 'negative':
            app.config['negative_count'] += 1
        elif parsed_tweet['sentiment'] == 'positive':
            app.config['positive_count'] += 1
        else:
            app.config['neutral_count'] += 1

        if parsed_tweet not in tweets:
            tweets.append(parsed_tweet)

    return tweets



@app.route('/')
def home():
    return render_template("index.html")

@app.route("/predict", methods=['POST', 'GET'])
def pred():

    if request.method == 'POST':
        query = request.form['query']
        count = request.form['num']
        
    count = int(count)



    fetched_tweets = get_tweets(api, query, count)

    print(app.config['neutral_count'] ,app.config['negative_count'],app.config['positive_count'])

    if fetched_tweets:
        return render_template('result.html', result=fetched_tweets,negative_count=app.config['negative_count'],positive_count=app.config['positive_count'],neutral_count=app.config['neutral_count'] )
    else:
        return render_template('result.html', result=[], message="No tweets found")


@app.route("/sentence", methods=['POST', 'GET'])
def predSentence():

    if request.method == 'POST':
        sentence = request.form['txt']

    sentiment = get_tweet_sentiment(sentence)
    polarity = get_tweet_polarity(sentence)

    if sentence:
        return render_template('result1.html', msg=sentence,result=sentiment,polarity=polarity)
    else:
        return render_template('result.html', result=[], message="Something went wrong!")

if __name__ == '__main__':
    app.run()