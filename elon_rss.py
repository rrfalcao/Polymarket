import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from flask import Flask, Response

app = Flask(__name__)

NITTER_URL = 'https://nitter.net/elonmusk'

@app.route('/rss')
def generate_rss():
    res = requests.get(NITTER_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    fg = FeedGenerator()
    fg.title("Elon Musk Tweets")
    fg.link(href="https://twitter.com/elonmusk")
    fg.description("Latest tweets from Elon Musk via Nitter")
    
    tweets = soup.find_all('div', class_='timeline-item')[:10]  # Most recent 10 tweets

    for tweet in tweets:
        content = tweet.find('div', class_='tweet-content').text.strip()
        link = 'https://twitter.com' + tweet.find('a', {'href': True})['href']
        time = tweet.find('span', class_='tweet-date').find('a')['title']

        fe = fg.add_entry()
        fe.title(content[:60] + '...')
        fe.link(href=link)
        fe.description(content)
        fe.pubDate(time)

    rssfeed = fg.rss_str(pretty=True)
    return Response(rssfeed, mimetype='application/rss+xml')

if __name__ == '__main__':
    app.run(port=5000)
