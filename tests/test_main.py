import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SAMPLE_POSTS = [{"subreddit": "datingover40", "title": "Test", "body": "", "score": 100,
                 "num_comments": 10, "engagement_score": 130, "feed_type": "hot", "top_comments": []}]

SAMPLE_ANALYSIS = {
    "trending_topics": ["topic1"], "pain_points": ["pain1"], "content_hooks": ["hook1"],
    "product_signals": ["signal1"], "exact_quotes": [], "power_phrases": ["phrase1"],
    "subreddit_breakdown": {}, "summary": "Summary text.",
}


def test_main_calls_all_three_stages():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "123",
    }
    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import main
        importlib.reload(main)

        with patch("src.main.collect_posts", return_value=SAMPLE_POSTS) as mock_scrape, \
             patch("src.main.analyze_posts", return_value=SAMPLE_ANALYSIS) as mock_analyze, \
             patch("src.main.send_digest") as mock_notify:
            main.run()

    mock_scrape.assert_called_once()
    mock_analyze.assert_called_once_with(SAMPLE_POSTS)
    mock_notify.assert_called_once_with(SAMPLE_ANALYSIS)


def test_main_exits_if_no_posts():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "123",
    }
    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import main
        importlib.reload(main)

        with patch("src.main.collect_posts", return_value=[]), \
             patch("src.main.analyze_posts") as mock_analyze, \
             patch("src.main.send_digest") as mock_notify:
            main.run()

    mock_analyze.assert_not_called()
    mock_notify.assert_not_called()
