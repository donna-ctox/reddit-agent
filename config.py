import os
from dotenv import load_dotenv

# override=False (default) means existing env vars take precedence over .env file,
# which keeps tests safe when using patch.dict(os.environ, ..., clear=True)
load_dotenv()

REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
REDDIT_USER_AGENT = os.environ["REDDIT_USER_AGENT"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

_default_subs = "datingover40,datingover30,Divorce,relationship_advice,DeadBedrooms,Marriage,BreakUps,dating_advice"
TARGET_SUBREDDITS = [
    s.strip()
    for s in os.environ.get("TARGET_SUBREDDITS", _default_subs).split(",")
    if s.strip()
]

MAX_POSTS_PER_SUB = int(os.environ.get("MAX_POSTS_PER_SUB", "25"))
