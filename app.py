import re
from textblob import TextBlob
from flask import Flask, render_template, request
from newsdataapi import NewsDataApiClient

app = Flask(__name__)
app.static_folder = 'static'

api = NewsDataApiClient(apikey='pub_34428f75ef514735b92c05edc03f3cbd6c309')


# ---------------- CLEAN TEXT ----------------
def clean_tweet(text):
    return ' '.join(
        re.sub(
            r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)",
            " ",
            text
        ).split()
    )


# ---------------- POLARITY ----------------
def get_tweet_polarity(text):
    analysis = TextBlob(clean_tweet(text))
    return analysis.sentiment.polarity


# ---------------- SENTIMENT WITH THRESHOLD ----------------
def get_tweet_sentiment(text):
    analysis = TextBlob(clean_tweet(text))
    polarity = analysis.sentiment.polarity

    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"


# ---------------- FETCH NEWS ----------------
def get_tweets(api, query, count):
    tweets = []

    # Reset counts for every request
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    response = api.news_api(q=query, language='en', size=count)

    for article in response.get('results', []):
        text = article.get('title', '')

        sentiment = get_tweet_sentiment(text)
        polarity = get_tweet_polarity(text)

        if sentiment == "positive":
            positive_count += 1
        elif sentiment == "negative":
            negative_count += 1
        else:
            neutral_count += 1

        tweets.append({
            'text': text,
            'sentiment': sentiment,
            'polarity': polarity,
            'date': article.get('pubDate', ''),
            'source_name': article.get('source_id', 'Unknown'),
            'link': article.get('link', '')
        })

    return tweets, positive_count, negative_count, neutral_count


# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return render_template("index.html")


@app.route("/predict", methods=['POST'])
def predict():
    query = request.form['query']
    count = int(request.form['num'])

    results, pos, neg, neu = get_tweets(api, query, count)

    return render_template(
        'result.html',
        result=results,
        positive_count=pos,
        negative_count=neg,
        neutral_count=neu
    )


@app.route("/sentence", methods=['POST'])
def predict_sentence():
    sentence = request.form['txt']

    sentiment = get_tweet_sentiment(sentence)
    polarity = get_tweet_polarity(sentence)

    return render_template(
        'result1.html',
        msg=sentence,
        result=sentiment,
        polarity=polarity
    )


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)
