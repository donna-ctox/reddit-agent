import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SAMPLE_POSTS = [
    {
        "subreddit": "datingover40",
        "title": "Dating after divorce at 45 feels impossible",
        "body": "I don't know how to meet people anymore",
        "score": 500,
        "num_comments": 80,
        "engagement_score": 740,
        "feed_type": "hot",
        "top_comments": ["Same here", "It gets better"],
    }
] * 5

SAMPLE_ANALYSIS = {
    "trending_topics": ["dating after divorce", "loneliness", "trust issues"],
    "pain_points": ["fear of vulnerability", "outdated dating apps"],
    "content_hooks": ["Why dating after 40 hits different"],
    "product_signals": ["coaching for re-entering dating scene"],
    "exact_quotes": [
        {
            "quote": "I don't know how to meet people anymore",
            "source": "r/datingover40",
            "why_it_matters": "Raw vulnerability that resonates widely",
            "category": "content",
        }
    ],
    "power_phrases": ["starting over", "emotionally unavailable"],
    "subreddit_breakdown": {"r/datingover40": "High volume of post-divorce dating posts"},
    "summary": "Women over 40 are navigating re-entry into dating with fear and hope.",
}


def make_mock_anthropic(response_json):
    mock_client = MagicMock()
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.get_final_text.return_value = json.dumps(response_json)
    mock_client.messages.stream.return_value = mock_stream
    return mock_client


def test_analyze_posts_returns_dict():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "123",
    }
    mock_client = make_mock_anthropic(SAMPLE_ANALYSIS)

    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import analyzer
        importlib.reload(analyzer)

        with patch("src.analyzer.anthropic.Anthropic", return_value=mock_client):
            result = analyzer.analyze_posts(SAMPLE_POSTS)

    assert isinstance(result, dict)
    assert "trending_topics" in result
    assert "pain_points" in result
    assert "content_hooks" in result
    assert "product_signals" in result
    assert "exact_quotes" in result
    assert "power_phrases" in result
    assert "subreddit_breakdown" in result
    assert "summary" in result


def test_analyze_posts_only_sends_top_40():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "123",
    }
    posts = [
        {
            "subreddit": "test", "title": f"Post {i}", "body": "",
            "score": i, "num_comments": i, "engagement_score": i * 4,
            "feed_type": "hot", "top_comments": [],
        }
        for i in range(60)
    ]
    mock_client = make_mock_anthropic(SAMPLE_ANALYSIS)
    captured_prompt = {}

    original_return_value = mock_client.messages.stream.return_value

    def capture_stream(*args, **kwargs):
        captured_prompt["messages"] = kwargs.get("messages", [])
        return original_return_value

    mock_client.messages.stream.side_effect = capture_stream

    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import analyzer
        importlib.reload(analyzer)

        with patch("src.analyzer.anthropic.Anthropic", return_value=mock_client):
            analyzer.analyze_posts(posts)

    prompt_text = captured_prompt["messages"][0]["content"]
    # Should include top 40 by engagement, not all 60
    sent_posts = json.loads(prompt_text.split("Posts data:\n")[1].split("\n\nReturn")[0])
    assert len(sent_posts) == 40


def test_analyze_posts_strips_markdown_fences():
    env = {
        "REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent", "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "123",
    }
    mock_client = MagicMock()
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    # Claude wraps JSON in markdown fences
    mock_stream.get_final_text.return_value = f"```json\n{json.dumps(SAMPLE_ANALYSIS)}\n```"
    mock_client.messages.stream.return_value = mock_stream

    with patch.dict(os.environ, env, clear=True):
        import config, importlib
        importlib.reload(config)
        from src import analyzer
        importlib.reload(analyzer)

        with patch("src.analyzer.anthropic.Anthropic", return_value=mock_client):
            result = analyzer.analyze_posts(SAMPLE_POSTS)

    assert "trending_topics" in result
