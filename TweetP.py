import pandas
from nltk.tokenize import TweetTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx
from math import log
from bokeh.palettes import viridis


with open('en_stopwords.txt','r') as enstop_file:
    enstop = set(enstop_file.read().split())
    
tweettokenizer = TweetTokenizer(preserve_case=False,
                                reduce_len=True,
                                strip_handles=True)

def extract_words(text):
    text=text.replace('#', ' ').replace('@', ' ')
    tokens=tweettokenizer.tokenize(text)
    return [item for item in tokens if item.isalpha()]
    
vectorizer = TfidfVectorizer(stop_words=enstop, min_df=2, ngram_range=(1,3),
                             binary=True, tokenizer=extract_words)

feature_cols = ['tweet_id', 'user_id', 'url',
                'popularity',
                'text', 'related_tweets']


def extract_feature(tweet):

    #process the outmost tweet
    features = [[tweet['id_str'], tweet['user']['id_str'],
                 'https://twitter.com/'+tweet['user']['id_str']+'/status/'+tweet['id_str'],
                 tweet['favorite_count']+tweet['retweet_count'],
                 tweet['text']]]

    # save the tweet_id and user_id that are related to the current tweet
    # either of reply_to, quoted, or retweet
    related_tweet = []
    if 'in_reply_to_status_id_str' in tweet:
        related_tweet.append((tweet['in_reply_to_status_id_str'],
                              tweet['in_reply_to_user_id_str']))
    features[0].append(related_tweet)

    # if a quote or retweet, examine the parent tweet
    if 'quoted_status' in tweet:
        related_tweet.append((tweet['quoted_status']['id_str'],
                              tweet['quoted_status']['user']['id_str']))
        features.extend(extract_feature(tweet['quoted_status']))
    elif 'retweet_status' in tweet:
        related_tweet.append((tweet['retweet_status']['id_str'],
                              tweet['retweet_status']['user']['id_str']))
        features.extend(extract_feature(tweet['retweet_status']))

    return features


def tweet_process(tweet_list):
    features = []
    for tweet in tweet_list:
        features.extend(extract_feature(tweet))
    tweet_feature = pandas.DataFrame(features, columns=feature_cols)
    
    topic_vectors = vectorizer.fit_transform(tweet_feature['text'])
    similarity = topic_vectors.dot(topic_vectors.transpose())
    
    nonz = similarity.nonzero()
    edges = zip(nonz[0], nonz[1], similarity[nonz].flat)
    edges_upper = (item for item in edges if item[0] > item[1])

    tweet_g = networkx.Graph()
    tweet_g.add_weighted_edges_from(edges_upper)
    spring_xy = networkx.spring_layout(tweet_g, iterations=50)

    tweet_feature['x'] = [0] * len(tweet_feature)
    tweet_feature['y'] = [0] * len(tweet_feature)
    for node, xy in spring_xy.items():
        tweet_feature.loc[node, 'x'] = xy[0]
        tweet_feature.loc[node, 'y'] = xy[1]

    tweet_feature['color'] = [0] * len(tweet_feature)
    maxpop = log(max(tweet_feature['popularity'])+1, 2)
    for i in range(len(tweet_feature)):
        tweet_feature.loc[i,'color']=viridis(256)[int(log(tweet_feature.loc[i,'popularity']+1,2)*255/maxpop)]

    return tweet_feature

if __name__ == "__main__":
    pass

    
