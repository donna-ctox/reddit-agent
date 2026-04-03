import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import anthropic
import config

SYSTEM_PROMPT = (
    "You are a market researcher and content strategist specializing in the emotional "
    "and relational lives of women aged 35-55. You pay close attention to the exact words "
    "and phrases this audience uses — their vocabulary, metaphors, and emotional language "
    "are as important as the topics themselves."
)

OUTPUT_SCHEMA = """{
  "trending_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
  "pain_points": ["pain1", "pain2", "pain3"],
  "content_hooks": ["hook1", "hook2", "hook3"],
  "product_signals": ["signal1", "signal2", "signal3"],
  "exact_quotes": [
    {
      "quote": "verbatim text from a post or comment",
      "source": "r/subreddit_name",
      "why_it_matters": "one line on why this language is useful",
      "category": "content"
    }
  ],
  "power_phrases": ["phrase1", "phrase2", "phrase3", "phrase4", "phrase5"],
  "subreddit_breakdown": {
    "r/subreddit": "one line summary of what's trending there"
  },
  "summary": "One paragraph executive summary of this week's relationship landscape for women 35-55"
}"""


def analyze_posts(posts):
    top_posts = sorted(posts, key=lambda p: p["engagement_score"], reverse=True)[:40]
    prompt = _build_prompt(top_posts)

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    for attempt in range(3):
        try:
            with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                text = stream.get_final_text()
            return _parse_response(text)
        except Exception as e:
            if "overloaded" in str(e).lower() and attempt < 2:
                wait = 30 * (attempt + 1)
                print(f"Claude overloaded, retrying in {wait}s...", flush=True)
                time.sleep(wait)
            else:
                raise


def _build_prompt(posts):
    posts_data = [
        {
            "subreddit": f"r/{p['subreddit']}",
            "title": p["title"],
            "body": p["body"],
            "score": p["score"],
            "comments": p["num_comments"],
            "engagement": p["engagement_score"],
            "top_comments": p["top_comments"],
        }
        for p in posts
    ]

    return f"""Analyze these Reddit posts from communities where women aged 35-55 discuss romantic relationships.

Posts data:
{json.dumps(posts_data, indent=2)}

Return ONLY a valid JSON object with this exact structure (no markdown, no commentary outside JSON):
{OUTPUT_SCHEMA}

Rules:
- exact_quotes: 5-8 verbatim quotes copied exactly from the posts or comments above. category must be "content" (for content strategy use) or "market" (for product/market research use)
- power_phrases: recurring words, phrases, or metaphors this audience uses repeatedly across multiple posts
- trending_topics: topics getting the most engagement and discussion volume
- pain_points: specific frustrations, fears, and unmet needs — be concrete, not generic
- product_signals: gaps, desires, and things they wish existed or wish worked better
- content_hooks: ready-to-use angles for posts, videos, or newsletters targeting this audience"""


def _parse_response(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Find the closing fence, if present
        if lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1])
        elif len(lines) > 1:
            text = "\n".join(lines[1:])
        else:
            raise ValueError(f"Malformed response: unclosed markdown fence: {text[:100]}")
    return json.loads(text)
