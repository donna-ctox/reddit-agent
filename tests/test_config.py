import os
import importlib
import pytest
from unittest.mock import patch


def test_config_loads_all_required_vars():
    env = {
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "TELEGRAM_BOT_TOKEN": "test_token",
        "TELEGRAM_CHAT_ID": "12345",
        "TARGET_SUBREDDITS": "datingover40,Divorce",
        "MAX_POSTS_PER_SUB": "20",
    }
    with patch.dict(os.environ, env, clear=True):
        import config
        importlib.reload(config)
        assert config.ANTHROPIC_API_KEY == "sk-ant-test"
        assert config.TELEGRAM_BOT_TOKEN == "test_token"
        assert config.TELEGRAM_CHAT_ID == "12345"
        assert config.TARGET_SUBREDDITS == ["datingover40", "Divorce"]
        assert config.MAX_POSTS_PER_SUB == 20


def test_config_default_subreddits():
    env = {
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


def test_config_raises_on_missing_required_var():
    import config
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(KeyError):
            importlib.reload(config)
