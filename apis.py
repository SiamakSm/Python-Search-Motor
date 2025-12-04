# apis.py
# Utility functions to fetch documents from Reddit and arXiv APIs.
#Add your API keys from the website so you can fetch data from these APIs


import praw
import urllib.request
import xmltodict
from datetime import datetime
from config import REDDIT_CLIENT_ID, REDDIT_SECRET, REDDIT_USER_AGENT

def fetch_reddit(keyword, limit=20):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    posts = reddit.subreddit("all").search(keyword, limit=limit)

    docs = []
    for post in posts:

        date_str = datetime.utcfromtimestamp(post.created_utc).strftime("%Y-%m-%d")

        docs.append({
            "titre": post.title,
            "auteur": str(post.author) if post.author else "Unknown",
            "date": date_str,
            "url": post.url,
            "texte": (post.selftext or "").replace("\n", " "),
            "type": "Reddit",
            "extra": post.num_comments
        })
    return docs


def fetch_arxiv(keyword, max_results=20):
    url = f"http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results={max_results}"

    data = urllib.request.urlopen(url).read()
    feed = xmltodict.parse(data)["feed"]

    entries = feed.get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]

    docs = []

    for entry in entries:
        titre = entry["title"].strip().replace("\n", " ")

        raw_auth = entry["author"]
        if isinstance(raw_auth, list):
            auteurs = [a["name"] for a in raw_auth]
        else:
            auteurs = [raw_auth["name"]]

        date_str = entry["published"][:10]
        texte = entry["summary"].strip().replace("\n", " ")

        docs.append({
            "titre": titre,
            "auteur": auteurs[0],
            "auteurs": auteurs,
            "date": date_str,
            "url": entry["id"],
            "texte": texte,
            "type": "Arxiv",
            "extra": "|".join(auteurs)
        })

    return docs