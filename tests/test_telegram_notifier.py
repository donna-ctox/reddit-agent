import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SAMPLE_ANALYSIS = {
    "trending_topics": ["dating after divorce", "loneliness at 45", "trust issues"],
    "pain_points": ["fear of vulnerability", "outdated apps", "meeting people IRL"],
    "content_hooks": ["Why dating after 40 hits different", "The invisible woman myth"],
    "product_signals": ["coaching for re-entering dating", "community for divorced women"],
    "exact_quotes": [
        {
            "quote": "I feel like I'm starting from scratch at 47",
            "source": "r/datingover40",
            "why_it_matters": "Captures the fresh-start anxiety perfectly",
            "category": "content",
        },
        {
            "quote": "Nobody builds products for women like us",
            "source": "r/Divorce",
            "why_it_matters": "Explicit product gap signal",
            "category": "market",
        },
    ],
    "power_phrases": ["starting over", "emotionally unavailable", "my worth"],
    "subreddit_breakdown": {
        "r/datingover40": "High volume of post-divorce re-entry posts",
        "r/Divorce": "Emotional processing and next-chapter planning",
    },
    "summary": "Women over 40 are navigating re-entry into dating with a mix of fear and determination.",
}


def make_mock_response(status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.raise_for_status = MagicMock()
    if status_code >= 400:
        mock_resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return mock_resp


def test_send_digest_makes_two_requests():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "test_token", "TELEGRAM_CHAT_ID": "99999",
    }
    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import telegram_notifier
        importlib.reload(telegram_notifier)

        with patch("src.telegram_notifier.httpx.post", return_value=make_mock_response()) as mock_post:
            with patch("src.telegram_notifier.time.sleep"):
                telegram_notifier.send_digest(SAMPLE_ANALYSIS)

    assert mock_post.call_count == 2


def test_first_message_contains_content_fields():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "test_token", "TELEGRAM_CHAT_ID": "99999",
    }
    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import telegram_notifier
        importlib.reload(telegram_notifier)

        with patch("src.telegram_notifier.httpx.post", return_value=make_mock_response()) as mock_post:
            with patch("src.telegram_notifier.time.sleep"):
                telegram_notifier.send_digest(SAMPLE_ANALYSIS)

    first_call_text = mock_post.call_args_list[0][1]["json"]["text"]
    assert "CONTENT DIGEST" in first_call_text
    assert "TRENDING TOPICS" in first_call_text
    assert "CONTENT HOOKS" in first_call_text
    assert "POWER PHRASES" in first_call_text
    assert "starting over" in first_call_text


def test_second_message_contains_market_fields():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "test_token", "TELEGRAM_CHAT_ID": "99999",
    }
    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import telegram_notifier
        importlib.reload(telegram_notifier)

        with patch("src.telegram_notifier.httpx.post", return_value=make_mock_response()) as mock_post:
            with patch("src.telegram_notifier.time.sleep"):
                telegram_notifier.send_digest(SAMPLE_ANALYSIS)

    second_call_text = mock_post.call_args_list[1][1]["json"]["text"]
    assert "MARKET INTEL" in second_call_text
    assert "PAIN POINTS" in second_call_text
    assert "PRODUCT SIGNALS" in second_call_text
    assert "SUMMARY" in second_call_text


def test_content_quotes_go_to_first_message_market_quotes_to_second():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "test_token", "TELEGRAM_CHAT_ID": "99999",
    }
    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import telegram_notifier
        importlib.reload(telegram_notifier)

        with patch("src.telegram_notifier.httpx.post", return_value=make_mock_response()) as mock_post:
            with patch("src.telegram_notifier.time.sleep"):
                telegram_notifier.send_digest(SAMPLE_ANALYSIS)

    first_text = mock_post.call_args_list[0][1]["json"]["text"]
    second_text = mock_post.call_args_list[1][1]["json"]["text"]

    assert "I feel like I'm starting from scratch at 47" in first_text
    assert "Nobody builds products for women like us" in second_text


def test_messages_under_4096_chars():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "test_token", "TELEGRAM_CHAT_ID": "99999",
    }
    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import telegram_notifier
        importlib.reload(telegram_notifier)

        with patch("src.telegram_notifier.httpx.post", return_value=make_mock_response()) as mock_post:
            with patch("src.telegram_notifier.time.sleep"):
                telegram_notifier.send_digest(SAMPLE_ANALYSIS)

    for call in mock_post.call_args_list:
        assert len(call[1]["json"]["text"]) <= 4000


def test_send_raises_on_http_error():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "test_token", "TELEGRAM_CHAT_ID": "99999",
    }
    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import telegram_notifier
        importlib.reload(telegram_notifier)

        with patch("src.telegram_notifier.httpx.post", return_value=make_mock_response(400)):
            with patch("src.telegram_notifier.time.sleep"):
                with pytest.raises(Exception):
                    telegram_notifier.send_digest(SAMPLE_ANALYSIS)
