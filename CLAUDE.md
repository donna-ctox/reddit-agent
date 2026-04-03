# Reddit Relationship Trends Agent

Scrapes Reddit for trending romantic relationship topics among women 35-55, analyzes with Claude, and sends two Telegram digests every Tuesday and Friday.

## Architecture

3-stage pipeline: `reddit_scraper.py` → `analyzer.py` → `telegram_notifier.py`, orchestrated by `main.py`.

## Running Locally

1. Copy `.env.example` to `.env` and fill in all values
2. Install: `pip3 install -r requirements.txt`
3. Run: `python3 src/main.py`

## Running Tests

```bash
python3 -m pytest -v
```

## GitHub Secrets Required

- `REDDIT_CLIENT_ID` — from reddit.com/prefs/apps
- `REDDIT_CLIENT_SECRET` — from reddit.com/prefs/apps
- `REDDIT_USER_AGENT` — e.g. `reddit-agent:v1.0 (by /u/your_username)`
- `ANTHROPIC_API_KEY` — from console.anthropic.com
- `TELEGRAM_BOT_TOKEN` — from @BotFather on Telegram
- `TELEGRAM_CHAT_ID` — your Telegram chat/channel ID

## GitHub Variables (Optional Overrides)

- `TARGET_SUBREDDITS` — comma-separated list (default: 8 subreddits defined in config.py)
- `MAX_POSTS_PER_SUB` — default 25

## Getting Reddit API Credentials

1. Go to reddit.com/prefs/apps
2. Click "create another app" at the bottom
3. Select "script"
4. Name it anything (e.g. "relationship-trends-agent")
5. Set redirect URI to `http://localhost:8080`
6. Copy the `client_id` (under the app name) and `client_secret`
7. Set `REDDIT_USER_AGENT` to something like: `reddit-agent:v1.0 (by /u/yourusername)`

## Schedule

Runs automatically every Tuesday and Friday at 9am UTC via GitHub Actions.
Manual runs: GitHub → Actions tab → "Reddit Relationship Digest" → "Run workflow".

## Two Telegram Messages Per Run

- **Message 1 (Content Strategy):** Trending topics, content hooks, exact quotes (content category), power phrases, subreddit pulse
- **Message 2 (Market Intel):** Pain points, product signals, exact quotes (market category), summary

## Subreddit List

r/datingover40, r/datingover30, r/Divorce, r/relationship_advice, r/DeadBedrooms, r/Marriage, r/BreakUps, r/dating_advice
