import os
import sys
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, "/Users/donnamccourt/reddit-agent")


def make_mock_submission(title, body, score, num_comments, sub="datingover40", created=1700000000.0):
    submission = MagicMock()
    submission.id = f"id_{title[:10]}"
    submission.title = title
    submission.selftext = body
    submission.score = score
    submission.num_comments = num_comments
    submission.upvote_ratio = 0.92
    submission.created_utc = created
    submission.subreddit.display_name = sub

    comment = MagicMock()
    comment.score = 50
    comment.body = "This really resonates with me"
    submission.comments.replace_more.return_value = []
    submission.comments.list.return_value = [comment]

    return submission


def make_mock_reddit(hot_posts, rising_posts, sub="datingover40"):
    reddit = MagicMock()
    subreddit = MagicMock()
    subreddit.hot.return_value = hot_posts
    subreddit.rising.return_value = rising_posts
    reddit.subreddit.return_value = subreddit
    return reddit


def test_collect_posts_returns_list():
    env = {
        "REDDIT_CLIENT_ID": "id",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent",
        "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "123",
        "TARGET_SUBREDDITS": "datingover40",
        "MAX_POSTS_PER_SUB": "5",
    }
    hot = [make_mock_submission("Hot post 1", "Body 1", 500, 30)]
    rising = [make_mock_submission("Rising post 1", "Body 2", 100, 10)]
    mock_reddit = make_mock_reddit(hot, rising)

    with patch.dict(os.environ, env, clear=True):
        import config
        import importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.praw.Reddit", return_value=mock_reddit):
            posts = reddit_scraper.collect_posts()

    assert isinstance(posts, list)
    assert len(posts) == 2


def test_engagement_score_calculation():
    env = {
        "REDDIT_CLIENT_ID": "id",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent",
        "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "123",
        "TARGET_SUBREDDITS": "datingover40",
        "MAX_POSTS_PER_SUB": "5",
    }
    hot = [make_mock_submission("Post", "Body", score=200, num_comments=50)]
    rising = []
    mock_reddit = make_mock_reddit(hot, rising)

    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.praw.Reddit", return_value=mock_reddit):
            posts = reddit_scraper.collect_posts()

    assert posts[0]["engagement_score"] == 200 + 50 * 3  # 350


def test_post_dict_has_required_fields():
    env = {
        "REDDIT_CLIENT_ID": "id",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent",
        "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "123",
        "TARGET_SUBREDDITS": "datingover40",
        "MAX_POSTS_PER_SUB": "5",
    }
    hot = [make_mock_submission("Test Post", "Test body content", 300, 20)]
    rising = []
    mock_reddit = make_mock_reddit(hot, rising)

    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.praw.Reddit", return_value=mock_reddit):
            posts = reddit_scraper.collect_posts()

    post = posts[0]
    assert "subreddit" in post
    assert "title" in post
    assert "body" in post
    assert "score" in post
    assert "num_comments" in post
    assert "engagement_score" in post
    assert "feed_type" in post
    assert "top_comments" in post


def test_body_truncated_to_500_chars():
    env = {
        "REDDIT_CLIENT_ID": "id",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent",
        "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "123",
        "TARGET_SUBREDDITS": "datingover40",
        "MAX_POSTS_PER_SUB": "5",
    }
    long_body = "x" * 1000
    hot = [make_mock_submission("Post", long_body, 100, 5)]
    rising = []
    mock_reddit = make_mock_reddit(hot, rising)

    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.praw.Reddit", return_value=mock_reddit):
            posts = reddit_scraper.collect_posts()

    assert len(posts[0]["body"]) <= 500


def test_duplicate_posts_across_hot_and_rising_are_deduplicated():
    env = {
        "REDDIT_CLIENT_ID": "id",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent",
        "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "123",
        "TARGET_SUBREDDITS": "datingover40",
        "MAX_POSTS_PER_SUB": "5",
    }
    same_post = make_mock_submission("Same Post", "Body", 300, 20)
    hot = [same_post]
    rising = [same_post]  # same object = same id
    mock_reddit = make_mock_reddit(hot, rising)

    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.praw.Reddit", return_value=mock_reddit):
            posts = reddit_scraper.collect_posts()

    assert len(posts) == 1
