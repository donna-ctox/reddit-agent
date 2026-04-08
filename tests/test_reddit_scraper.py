import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def make_pullpush_response(posts_data):
    return {"data": posts_data}


def make_post_data(post_id, title, body="", score=100, num_comments=10,
                   upvote_ratio=0.92, created=1700000000):
    return {
        "id": post_id,
        "title": title,
        "selftext": body,
        "score": score,
        "num_comments": num_comments,
        "upvote_ratio": upvote_ratio,
        "created_utc": created,
    }


def make_mock_get(hot_posts, rising_posts):
    call_count = {"n": 0}

    def mock_get(url, **kwargs):
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.url = url
        response.status_code = 200
        params = kwargs.get("params", {})
        if params.get("sort_type") == "score":
            response.json.return_value = make_pullpush_response(hot_posts)
        else:
            response.json.return_value = make_pullpush_response(rising_posts)
        return response

    return mock_get


_BASE_ENV = {
    "ANTHROPIC_API_KEY": "key",
    "TELEGRAM_BOT_TOKEN": "token",
    "TELEGRAM_CHAT_ID": "123",
    "TARGET_SUBREDDITS": "datingover40",
    "MAX_POSTS_PER_SUB": "5",
}


def test_collect_posts_returns_list():
    hot = [make_post_data("id1", "Hot post 1", "Body 1", 500, 30)]
    rising = [make_post_data("id2", "Rising post 1", "Body 2", 100, 10)]

    with patch.dict(os.environ, _BASE_ENV, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.requests.get", side_effect=make_mock_get(hot, rising)):
            with patch("src.reddit_scraper.time.sleep"):
                posts = reddit_scraper.collect_posts()

    assert isinstance(posts, list)
    assert len(posts) == 2


def test_engagement_score_calculation():
    hot = [make_post_data("id1", "Post", "Body", score=200, num_comments=50)]
    rising = []

    with patch.dict(os.environ, _BASE_ENV, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.requests.get", side_effect=make_mock_get(hot, rising)):
            with patch("src.reddit_scraper.time.sleep"):
                posts = reddit_scraper.collect_posts()

    assert posts[0]["engagement_score"] == 200 + 50 * 3  # 350


def test_post_dict_has_required_fields():
    hot = [make_post_data("id1", "Test Post", "Test body content", 300, 20)]
    rising = []

    with patch.dict(os.environ, _BASE_ENV, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.requests.get", side_effect=make_mock_get(hot, rising)):
            with patch("src.reddit_scraper.time.sleep"):
                posts = reddit_scraper.collect_posts()

    post = posts[0]
    for field in ["subreddit", "title", "body", "score", "num_comments",
                  "engagement_score", "feed_type", "top_comments", "upvote_ratio", "created_utc"]:
        assert field in post


def test_body_truncated_to_500_chars():
    hot = [make_post_data("id1", "Post", "x" * 1000, 100, 5)]
    rising = []

    with patch.dict(os.environ, _BASE_ENV, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.requests.get", side_effect=make_mock_get(hot, rising)):
            with patch("src.reddit_scraper.time.sleep"):
                posts = reddit_scraper.collect_posts()

    assert len(posts[0]["body"]) <= 500


def test_duplicate_posts_across_hot_and_rising_are_deduplicated():
    same_post = make_post_data("same_id", "Same Post", "Body", 300, 20)
    hot = [same_post]
    rising = [same_post]

    with patch.dict(os.environ, _BASE_ENV, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.requests.get", side_effect=make_mock_get(hot, rising)):
            with patch("src.reddit_scraper.time.sleep"):
                posts = reddit_scraper.collect_posts()

    assert len(posts) == 1


def test_failed_subreddit_is_skipped():
    env = {**_BASE_ENV, "TARGET_SUBREDDITS": "datingover40,badsubreddit"}
    good_post = make_post_data("id1", "Good post", "Body", 100, 10)

    call_state = {"subs_seen": []}

    def mock_get_with_failure(url, **kwargs):
        params = kwargs.get("params", {})
        sub = params.get("subreddit", "")
        if sub == "badsubreddit":
            raise Exception("subreddit not found")
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.url = url
        response.status_code = 200
        if params.get("sort_type") == "score":
            response.json.return_value = make_pullpush_response([good_post])
        else:
            response.json.return_value = make_pullpush_response([])
        return response

    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import reddit_scraper
        importlib.reload(reddit_scraper)

        with patch("src.reddit_scraper.requests.get", side_effect=mock_get_with_failure):
            with patch("src.reddit_scraper.time.sleep"):
                posts = reddit_scraper.collect_posts()

    assert len(posts) == 1
    assert posts[0]["subreddit"] == "datingover40"
