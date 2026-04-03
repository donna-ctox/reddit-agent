import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reddit_scraper import collect_posts
from src.analyzer import analyze_posts
from src.telegram_notifier import send_digest


def run():
    print("Collecting Reddit posts...", flush=True)
    posts = collect_posts()
    print(f"Collected {len(posts)} posts.", flush=True)

    if not posts:
        print("No posts collected. Exiting.", flush=True)
        return

    print("Analyzing with Claude...", flush=True)
    analysis = analyze_posts(posts)
    print("Analysis complete.", flush=True)

    print("Sending Telegram digest...", flush=True)
    send_digest(analysis)
    print("Done.", flush=True)


if __name__ == "__main__":
    run()
