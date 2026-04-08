import sys
import os
import time
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import config

_HEADERS = {"User-Agent": "reddit-relationship-agent/1.0"}
_BASE = "https://api.pullpush.io/reddit/search/submission"


def collect_posts():
    all_posts = []
    for subreddit_name in config.TARGET_SUBREDDITS:
        try:
            posts = _scrape_subreddit(subreddit_name)
            print(f"r/{subreddit_name}: {len(posts)} posts", flush=True)
            all_posts.extend(posts)
        except Exception as e:
            print(f"Warning: skipping r/{subreddit_name} — {e}", flush=True)
    return all_posts


def _fetch_json(url, params):
    resp = requests.get(url, headers=_HEADERS, params=params, timeout=30)
    print(f"  GET {resp.url} → {resp.status_code}", flush=True)
    resp.raise_for_status()
    time.sleep(1)
    return resp.json()


def _scrape_subreddit(subreddit_name):
    now = datetime.now(timezone.utc)
    week_ago = int((now - timedelta(days=7)).timestamp())
    day_ago = int((now - timedelta(days=1)).timestamp())

    # "Hot": top-scoring posts from the last 7 days
    hot_data = _fetch_json(_BASE, {
        "subreddit": subreddit_name,
        "size": int(config.MAX_POSTS_PER_SUB * 0.6),
        "sort_type": "score",
        "sort": "desc",
        "after": week_ago,
    })

    # "Rising": most-commented posts from the last 24 hours
    rising_data = _fetch_json(_BASE, {
        "subreddit": subreddit_name,
        "size": config.MAX_POSTS_PER_SUB - int(config.MAX_POSTS_PER_SUB * 0.6),
        "sort_type": "num_comments",
        "sort": "desc",
        "after": day_ago,
    })

    hot_ids = {p["id"] for p in hot_data.get("data", [])}

    seen_ids = set()
    posts = []

    for post_data, feed_label in (
        [(p, "hot") for p in hot_data.get("data", [])] +
        [(p, "rising") for p in rising_data.get("data", [])]
    ):
        pid = post_data.get("id", "")
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)

        score = post_data.get("score", 0)
        num_comments = post_data.get("num_comments", 0)
        feed_type = "hot" if pid in hot_ids else "rising"

        posts.append({
            "subreddit": subreddit_name,
            "title": post_data.get("title", ""),
            "body": (post_data.get("selftext") or "")[:500],
            "score": score,
            "num_comments": num_comments,
            "upvote_ratio": post_data.get("upvote_ratio", 0),
            "created_utc": post_data.get("created_utc", 0),
            "engagement_score": score + num_comments * 3,
            "feed_type": feed_type,
            "top_comments": [],
        })

    return posts
