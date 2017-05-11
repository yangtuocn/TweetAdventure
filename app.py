from flask import Flask, request, render_template
import os

from requests_oauthlib import OAuth1

import math
import TweetP
import requests
import simplejson as json

from bokeh.palettes import viridis
from bokeh.embed import components
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool, TapTool, OpenURL, LogColorMapper, ColorBar, LogTicker


DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)


def build_plot(tweet_feature):

    tweet_source = ColumnDataSource(data=dict(x=tweet_feature['x'],
                                    y=tweet_feature['y'],
                                    text=tweet_feature['text'],
                                    url=tweet_feature['url'],
                                    color=tweet_feature['color']))

    p = figure(plot_width=600, plot_height=600,
               tools=[HoverTool(tooltips="""<div style="width:300px">@text</div>"""),
                       TapTool()],
               toolbar_location=None,
               title='hover to view tweet text, click to view tweet in a pop-up window')
    tap = p.select(type=TapTool)
    tap.callback = OpenURL(url='@url')
    p.axis.visible = False
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    color_mapper=LogColorMapper(palette='Viridis256',
                                low=1, high=max(tweet_feature['popularity'])+1)
    color_bar=ColorBar(color_mapper=color_mapper, ticker=LogTicker(),
                       label_standoff=6, border_line_color=None, location=(0,0),
                       title="likes")

    p.circle(x='x', y='y', source=tweet_source, size=8,
              fill_color='color', line_color='color')
    p.add_layout(color_bar, 'right')
    
    return components(p)


################################################################


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_query():
    
    tweet_query_keyword = request.form['tweet_query']
    tweet_query_result = requests.get('https://api.twitter.com/1.1/search/tweets.json',
                                      auth=my_auth,
                                      params={'q': tweet_query_keyword,
                                              'lang': 'en',
                                              'count': '100'}
                                      )
    tweet_list = tweet_query_result.json()['statuses']
    tweet_feature = TweetP.tweet_process(tweet_list)
    (scr, di) = build_plot(tweet_feature)
    
    return render_template('index.html',
                           key_word = 'Query: ' + tweet_query_keyword,
                           plot_script=scr,
                           plot_div=di)


if __name__ == "__main__":

    # set up twitter access token #
    with(open('config.txt','r')) as config:
        secrets = json.loads(config.read())

    my_auth = OAuth1(
        secrets["api_key"],
        secrets["api_secret"],
        secrets["access_token"],
        secrets["access_token_secret"]
    )
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '0.0.0.0', port = port)
    #app.run()
