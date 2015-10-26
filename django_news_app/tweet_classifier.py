### Set Twitter and MonkeyLearn API credentials

# You can get Twitter API credentials [by signing in with your Twitter account](https://apps.twitter.com) and then registering an app.

# TWITTER SETTINGS
# Put here your credentials to consume Twitter API
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_TOKEN_KEY = ''
TWITTER_ACCESS_TOKEN_SECRET = ''
MAXIMUM_TWEETS_PER_NEWS_CHANNEL = 200

# You can [signup with MonkeyLearn](http://www.monkeylearn.com/) and get your [API token](https://app.monkeylearn.com/accounts/user/settings/).

# MONKEYLEARN SETTINGS
# Put here your MonkeyLearn API token
MONKEYLEARN_TOKEN = '622fd47ba28e0edbd241c1747bcc06fa600a4c2f'

MONKEYLEARN_CLASSIFIER_BASE_URL = 'https://api.monkeylearn.com/api/v1/categorizer/'
MONKEYLEARN_EXTRACTOR_BASE_URL = 'https://api.monkeylearn.com/api/v1/extraction/'

# This classifier is used to detect the tweet/bio's language
MONKEYLEARN_LANG_CLASSIFIER_ID = 'cl_hDDngsX8'

# This classifier is used to detect the tweet/bio's topics
MONKEYLEARN_TOPIC_CLASSIFIER_ID = 'cl_5icAVzKR'

# This extractor is used to extract keywords from tweets and bios
MONKEYLEARN_EXTRACTOR_ID = 'ex_y7BPYzNG'


### Get user data with Twitter API

# tweepy is used to call the Twitter API from Python
import tweepy
import re
import requests
import json
from random import shuffle
from collections import Counter,defaultdict

def get_tweets(api, twitter_user,  max_tweets=200, min_words=5):
    tweets = []
    
    full_tweets = []
    step = 200  # Maximum value is 200.
    for start in xrange(0, max_tweets, step):
        end = start + step
        
        # Maximum of `step` tweets, or the remaining to reach max_tweets.
        count = min(step, max_tweets - start)

        kwargs = {'count': count}
        if full_tweets:
            last_id = full_tweets[-1].id
            kwargs['max_id'] = last_id - 1

        current = api.user_timeline(twitter_user, **kwargs)
    
        full_tweets.extend(current)
    
    for tweet in full_tweets:
        text = re.sub(r'(https?://\S+)', '', tweet.text)
        
        # Only tweets with at least five words.
        if len(re.split(r'[^0-9A-Za-z]+', text)) > min_words:
            tweets.append(text)
    return tweets

# This is a handy function to classify a list of texts in batch mode (much faster)
def classify_batch(text_list, classifier_id):
    """
    Batch classify texts
    text_list -- list of texts to be classified
    classifier_id -- id of the MonkeyLearn classifier to be applied to the texts
    """
    results = []
    
    step = 250
    for start in xrange(0, len(text_list), step):
        end = start + step

        data = {'text_list': text_list[start:end]}

        response = requests.post(
            MONKEYLEARN_CLASSIFIER_BASE_URL + classifier_id + '/classify_batch_text/',
            data=json.dumps(data),
            headers={
                'Authorization': 'Token {}'.format(MONKEYLEARN_TOKEN),
                'Content-Type': 'application/json'
        })
        
        try:
            results.extend(response.json()['result'])
        except:
            raise

    return results


def filter_language(texts, language='English'):
    
    # Get the language of the tweets and bios using Monkeylearn's Language classifier
    lang_classifications = classify_batch(texts, MONKEYLEARN_LANG_CLASSIFIER_ID)
    
    # Only keep the descriptions that are writtern in English.
    lang_texts = [
        text
        for text, prediction in zip(texts, lang_classifications)
        if prediction[0]['label'] == language
    ]

    return lang_texts

### Detect the topics with MonkeyLearn API
def category_histogram(texts, short_texts):
    # Classify the bios and tweets with MonkeyLearn's news classifier.
    topics = classify_batch(texts, MONKEYLEARN_TOPIC_CLASSIFIER_ID)
    
    # The histogram will keep the counters of how many texts fall in
    # a given category.
    histogram = Counter()
    samples = defaultdict(list)

    for classification, text, short_text in zip(topics, texts, short_texts):

        # Join the parent and child category names in one string.
        category = classification[0]['label']
        probability = classification[0]['probability']
        
        if len(classification) > 1:
            category += '/' + classification[1]['label']
            probability *= classification[1]['probability']
        
        MIN_PROB = 0.0
        # Discard texts with a predicted topic with probability lower than a treshold
        if probability < MIN_PROB:
            continue
        
        # Increment the category counter.
        histogram[category] += 1
        
        # Store the texts by category
        samples[category].append(text)
        
    return histogram, samples

def extract_keywords(text_list, max_keywords):
    results = []
    step = 250
    for start in xrange(0, len(text_list), step):
        end = start + step

        data = {'text_list': text_list[start:end],
                'max_keywords': max_keywords}

        response = requests.post(
            MONKEYLEARN_EXTRACTOR_BASE_URL + MONKEYLEARN_EXTRACTOR_ID + '/extract_batch_text/',
            data=json.dumps(data),
            headers={
                'Authorization': 'Token {}'.format(MONKEYLEARN_TOKEN),
                'Content-Type': 'application/json'
        })

        try:
            results.extend(response.json()['result'])
        except:
            raise

    return results


import multiprocessing.dummy as multiprocessing

BING_KEY = ''
EXPAND_TWEETS = False

def _bing_search(query):
    MAX_EXPANSIONS = 5
    
    params = {
        'Query': u"'{}'".format(query),
        '$format': 'json',
    }
    
    response = requests.get(
        'https://api.datamarket.azure.com/Bing/Search/v1/Web',
        params=params,
        auth=(BING_KEY, BING_KEY)
    )
    
    try:    
        response = response.json()
    except ValueError as e:
        texts = []
        return
    else:
        texts = []
        for result in response['d']['results'][:MAX_EXPANSIONS]:
            texts.append(result['Title'])
            texts.append(result['Description'])

    return u" ".join(texts)


def _expand_text(text):
    result = text + u"\n" + _bing_search(text)
    return result


def expand_texts(texts):
    # First extract hashtags and keywords from the text to form the queries
    queries = []
    keyword_list = extract_keywords(texts, 10)
    for text, keywords in zip(texts, keyword_list):
        query = ' '.join([item['keyword'] for item in keywords])
        query = query.lower()
        tags = re.findall(r"#(\w+)", text)
        for tag in tags:
            tag = tag.lower()
            if tag not in query:
                query = tag + ' ' + query
        queries.append(query)
        
    pool = multiprocessing.Pool(2)
    return pool.map(_expand_text, queries)


def classify_tweets(newsaccount):
    # Authenticate to Twitter API
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    tweets = get_tweets(api,newsaccount,MAXIMUM_TWEETS_PER_NEWS_CHANNEL)
    tweets_english = filter_language(tweets)
    if EXPAND_TWEETS:
        expanded_tweets = expand_texts(tweets_english)
    else:
        expanded_tweets = tweets_english
    tweets_histogram, tweets_categorized = category_histogram(tweets, expanded_tweets)
    return tweets_categorized, tweets_histogram

