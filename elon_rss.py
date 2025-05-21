import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from flask import Flask, Response

app = Flask(__name__)

# List of fallback Nitter instances (ordered by reliability)
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.tiekoetter.com",
    "https://nitter.kavin.rocks",
    "https://nitter.privacyredirect.com",
    "https://nitter.pussthecat.org",
    "https://nitter.42l.fr",
]

def fetch_nitter_html(username="elonmusk"):
    for base_url in NITTER_INSTANCES:
        try:
            full_url = f"{base_url}/{username}"
            print(f"Trying Nitter instance: {full_url}")
            response = requests.get(full_url, timeout=5)
            if response.ok and "tweet-content" in response.text:
                return response.text
        except Exception as e:
            print(f"Failed to fetch from {base_url}: {e}")
            continue
    raise RuntimeError("All Nitter instances failed.")

@app.route("/")
def index():
    return "✅ Elon Musk RSS feed is running. Visit /rss to get the feed."

@app.route("/rss")
def generate_rss():
    try:
        html = fetch_nitter_html("elonmusk")
        soup = BeautifulSoup(html, 'html.parser')

        fg = FeedGenerator()
        fg.title("Elon Musk Tweets")
        fg.link(href="https://twitter.com/elonmusk")
        fg.description("Latest tweets from Elon Musk via Nitter")

        tweets = soup.find_all('div', class_='timeline-item')[:10]

        if not tweets:
            raise ValueError("No tweets found — Nitter may be down or blocked.")

        for tweet in tweets:
            content_div = tweet.find('div', class_='tweet-content')
            date_link = tweet.find('span', class_='tweet-date').find('a')

            if not content_div or not date_link:
                continue

            content = content_div.text.strip()
            link = 'https://twitter.com' + date_link['href']
            time = date_link['title']

            fe = fg.add_entry()
            fe.title(content[:60] + '...')
            fe.link(href=link)
            fe.description(content)
            fe.pubDate(time)

        return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')

    except Exception as e:
        return f"<h1>Internal Server Error</h1><p>{str(e)}</p>", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
