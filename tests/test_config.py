import os
import importlib
from unittest.mock import patch


def test_config_loads_all_required_vars():
    env = {
        "REDDIT_CLIENT_ID": "test_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "TELEGRAM_BOT_TOKEN": "test_token",
        "TELEGRAM_CHAT_ID": "12345",
        "TARGET_SUBREDDITS": "datingover40,Divorce",
        "MAX_POSTS_PER_SUB": "20",
    }
    with patch.dict(os.environ, env, clear=True):
        import config
        importlib.reload(config)
        assert config.REDDIT_CLIENT_ID == "test_id"
        assert config.REDDIT_CLIENT_SECRET == "test_secret"
        assert config.REDDIT_USER_AGENT == "test_agent"
        assert config.ANTHROPIC_API_KEY == "sk-ant-test"
        assert config.TELEGRAM_BOT_TOKEN == "test_token"
        assert config.TELEGRAM_CHAT_ID == "12345"
        assert config.TARGET_SUBREDDITS == ["datingover40", "Divorce"]
        assert config.MAX_POSTS_PER_SUB == 20


def test_config_default_subreddits():
    env = {
        "REDDIT_CLIENT_ID": "id",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "agent",
        "ANTHROPIC_API_KEY": "key",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "123",
    }
    with patch.dict(os.environ, env, clear=True):
        import config
        importlib.reload(config)
        assert "datingover40" in config.TARGET_SUBREDDITS
        assert len(config.TARGET_SUBREDDITS) == 8
        assert config.MAX_POSTS_PER_SUB == 25
