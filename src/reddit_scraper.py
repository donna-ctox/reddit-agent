import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import praw
import config


def collect_posts():
    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )

    all_posts = []
    for subreddit_name in config.TARGET_SUBREDDITS:
        try:
            posts = _scrape_subreddit(reddit, subreddit_name)
            all_posts.extend(posts)
        except Exception as e:
            print(f"Warning: skipping r/{subreddit_name} — {e}", flush=True)

    return all_posts


def _scrape_subreddit(reddit, subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    hot_limit = int(config.MAX_POSTS_PER_SUB * 0.6)
    rising_limit = config.MAX_POSTS_PER_SUB - hot_limit
    hot_posts = list(subreddit.hot(limit=hot_limit))
    rising_posts = list(subreddit.rising(limit=rising_limit))
    hot_ids = {s.id for s in hot_posts}

    seen_ids = set()
    posts = []

    for submission in hot_posts + rising_posts:
        if submission.id in seen_ids:
            continue
        seen_ids.add(submission.id)

        feed_type = "hot" if submission.id in hot_ids else "rising"
        top_comments = _get_top_comments(submission)
        engagement_score = submission.score + submission.num_comments * 3

        posts.append({
            "subreddit": subreddit_name,
            "title": submission.title,
            "body": (submission.selftext or "")[:500],
            "score": submission.score,
            "num_comments": submission.num_comments,
            "upvote_ratio": submission.upvote_ratio,
            "created_utc": submission.created_utc,
            "engagement_score": engagement_score,
            "feed_type": feed_type,
            "top_comments": top_comments,
        })

    return posts


def _get_top_comments(submission):
    try:
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()
        ranked = sorted(
            [c for c in comments if hasattr(c, "body") and hasattr(c, "score")],
            key=lambda c: c.score,
            reverse=True,
        )
        return [c.body[:300] for c in ranked[:3]]
    except Exception as e:
        print(f"Warning: could not fetch comments — {e}", flush=True)
        return []
