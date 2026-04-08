import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import config

_HEADERS = {"User-Agent": "reddit-relationship-agent/1.0"}
_BASE = "https://www.reddit.com"


def collect_posts():
    all_posts = []
    for subreddit_name in config.TARGET_SUBREDDITS:
        try:
            posts = _scrape_subreddit(subreddit_name)
            all_posts.extend(posts)
        except Exception as e:
            print(f"Warning: skipping r/{subreddit_name} — {e}", flush=True)
    return all_posts


def _fetch_json(url):
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    time.sleep(1)
    return resp.json()


def _scrape_subreddit(subreddit_name):
    hot_limit = int(config.MAX_POSTS_PER_SUB * 0.6)
    rising_limit = config.MAX_POSTS_PER_SUB - hot_limit

    hot_data = _fetch_json(f"{_BASE}/r/{subreddit_name}/hot.json?limit={hot_limit}&raw_json=1")
    rising_data = _fetch_json(f"{_BASE}/r/{subreddit_name}/rising.json?limit={rising_limit}&raw_json=1")

    hot_children = hot_data["data"]["children"]
    rising_children = rising_data["data"]["children"]
    hot_ids = {c["data"]["id"] for c in hot_children}

    seen_ids = set()
    posts = []

    for child in hot_children + rising_children:
        post_data = child["data"]
        pid = post_data["id"]
        if pid in seen_ids:
            continue
        seen_ids.add(pid)

        score = post_data.get("score", 0)
        num_comments = post_data.get("num_comments", 0)

        posts.append({
            "_id": pid,
            "subreddit": subreddit_name,
            "title": post_data.get("title", ""),
            "body": (post_data.get("selftext") or "")[:500],
            "score": score,
            "num_comments": num_comments,
            "upvote_ratio": post_data.get("upvote_ratio", 0),
            "created_utc": post_data.get("created_utc", 0),
            "engagement_score": score + num_comments * 3,
            "feed_type": "hot" if pid in hot_ids else "rising",
            "top_comments": [],
        })

    # Fetch comments only for top 5 posts to limit request count
    top_posts = sorted(posts, key=lambda p: p["engagement_score"], reverse=True)[:5]
    for post in top_posts:
        post["top_comments"] = _get_top_comments(subreddit_name, post["_id"])

    for post in posts:
        del post["_id"]

    return posts


def _get_top_comments(subreddit_name, post_id):
    try:
        data = _fetch_json(
            f"{_BASE}/r/{subreddit_name}/comments/{post_id}.json?limit=10&raw_json=1"
        )
        comments_listing = data[1]["data"]["children"]
        comments = [
            c["data"] for c in comments_listing
            if c.get("kind") == "t1" and c["data"].get("body")
        ]
        ranked = sorted(comments, key=lambda c: c.get("score", 0), reverse=True)
        return [c["body"][:300] for c in ranked[:3]]
    except Exception as e:
        print(f"Warning: could not fetch comments — {e}", flush=True)
        return []
