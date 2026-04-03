import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
import httpx
import config

TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage"
MAX_CHARS = 4000  # leave buffer under 4096


def send_digest(analysis):
    date_str = datetime.utcnow().strftime("%a %b %d, %Y")
    msg1 = _format_content_message(analysis, date_str)
    msg2 = _format_market_message(analysis, date_str)
    _send(msg1)
    time.sleep(2)
    _send(msg2)


def _send(text):
    url = TELEGRAM_URL.format(config.TELEGRAM_BOT_TOKEN)
    resp = httpx.post(
        url,
        json={"chat_id": config.TELEGRAM_CHAT_ID, "text": text},
        timeout=15,
    )
    resp.raise_for_status()


def _format_content_message(analysis, date_str):
    lines = [
        "✍️ REDDIT CONTENT DIGEST",
        f"Women 35-55 | {date_str}",
        "",
        "🔥 TRENDING TOPICS",
    ]
    for topic in analysis.get("trending_topics", []):
        lines.append(f"• {topic}")

    lines.extend(["", "✍️ CONTENT HOOKS"])
    for hook in analysis.get("content_hooks", []):
        lines.append(f"• {hook}")

    content_quotes = [q for q in analysis.get("exact_quotes", []) if q.get("category") == "content"]
    if content_quotes:
        lines.extend(["", "💬 EXACT QUOTES"])
        for q in content_quotes:
            lines.append(f'"{q["quote"]}" — {q["source"]}')
            lines.append(f'↳ {q["why_it_matters"]}')

    phrases = analysis.get("power_phrases", [])
    if phrases:
        lines.extend(["", "🗣️ POWER PHRASES"])
        lines.append(" • ".join(f'"{p}"' for p in phrases))

    breakdown = analysis.get("subreddit_breakdown", {})
    if breakdown:
        lines.extend(["", "📍 SUBREDDIT PULSE"])
        for sub, summary in breakdown.items():
            lines.append(f"{sub}: {summary}")

    return _truncate("\n".join(lines))


def _format_market_message(analysis, date_str):
    lines = [
        "💡 REDDIT MARKET INTEL",
        f"Women 35-55 | {date_str}",
        "",
        "💔 PAIN POINTS",
    ]
    for pain in analysis.get("pain_points", []):
        lines.append(f"• {pain}")

    lines.extend(["", "🛍️ PRODUCT SIGNALS"])
    for signal in analysis.get("product_signals", []):
        lines.append(f"• {signal}")

    market_quotes = [q for q in analysis.get("exact_quotes", []) if q.get("category") == "market"]
    if market_quotes:
        lines.extend(["", "💬 EXACT QUOTES"])
        for q in market_quotes:
            lines.append(f'"{q["quote"]}" — {q["source"]}')
            lines.append(f'↳ {q["why_it_matters"]}')

    summary = analysis.get("summary", "")
    if summary:
        lines.extend(["", "📝 SUMMARY", summary])

    return _truncate("\n".join(lines))


def _truncate(text):
    if len(text) <= MAX_CHARS:
        return text
    return text[:MAX_CHARS] + "\n... [truncated]"
