# TweetAdventure
TweetAdventure is a visualization tool for exploratory tweet analysis.
http://tweetadventure-yangc.herokuapp.com/

TweetAdventure retrieves real-time tweets through Twitter Rest API 
upon user request, extracts topics using natural language analysis, 
builds feature vectors, and calculates cosine similarities among 
tweet pairs. The end product is a force-directed graph that uses 
nodes to represent tweets and clusters similar tweets together. 
The color scale of the nodes represents the total number of favorites
and retweets).

The graph shows at a glance the number of topics and the tweets
in each group. Viewers can click on what they like and dive into
related twitter pages.
