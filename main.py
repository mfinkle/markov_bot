import os
from xml.etree import ElementTree as etree
import urllib.request
import json
from datetime import datetime

import markovify
import pytumblr

from dotenv import load_dotenv
load_dotenv()

buzzfeed_corpus = []
buzzfeed_url = 'https://www.buzzfeed.com/lol.xml'

programming_corpus = []
programming_url = ['https://www.thecrazyprogrammer.com/feed', 'https://dev.to/rss']


request = urllib.request.Request(buzzfeed_url)
request.add_header('User-Agent', 'markovbot/1.0')
content = urllib.request.urlopen(request).read()
tree = etree.fromstring(content)
articles = tree.findall('channel/item')
if len(articles) > 0:
    for article in articles:
        # print('**', article.findtext('title'))
        buzzfeed_corpus.append(article.findtext('title'))

# print('=========')

for url in programming_url:
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'markovbot/1.0')
    content = urllib.request.urlopen(request).read()
    tree = etree.fromstring(content)
    articles = tree.findall('channel/item')
    if len(articles) > 0:
        for article in articles:
            # print('**', article.findtext('title'))
            programming_corpus.append(article.findtext('title'))


# Build the model
buzzfeed_model = markovify.NewlineText('\n'.join(buzzfeed_corpus), state_size=1)
programming_model = markovify.NewlineText('\n'.join(programming_corpus), state_size=1)
text_model = markovify.combine([buzzfeed_model, programming_model], [1, 2])

# Print five randomly-generated sentences
headlines = []
for i in range(5):
    headline = text_model.make_sentence()
    if headline is not None:
        headlines.append('* ' + headline)
        print(headline)

if len(headlines) > 0:
    # Post to Tumblr
    client = pytumblr.TumblrRestClient(
        os.getenv('CONSUMER_KEY'),
        os.getenv('CONSUMER_SECRET'),
        os.getenv('OAUTH_TOKEN'),
        os.getenv('OAUTH_SECRET'),
    )

    blog = 'markovfinkle'
    title = 'Today\'s Headlines'
    slug = 'todays-headlines-' + datetime.utcnow().strftime('%Y%m%d%H%M%S')
    body = '\n'.join(headlines)
    client.create_text(blog, state='published', title=title, body=body, format='markdown', slug=slug)
