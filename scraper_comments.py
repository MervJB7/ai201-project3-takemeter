"""
scrape_comments.py
Pulls r/nba COMMENTS from the Arctic Shift API. Comments are where the
analysis / hot_take / reaction content actually lives — posts are mostly
news links and game threads, which is why post-scraping stalls out.

Outputs nba_comments_raw.csv with a single `text` column (unlabeled).
You label it afterward (manually or LLM-assisted-then-reviewed).
"""

import requests
import csv
import time

HEADERS = {"User-Agent": "Mozilla/5.0 (takemeter-project)"}
BASE = "https://arctic-shift.photon-reddit.com/api/comments/search"

# Several windows so you get variety across different news cycles.
# 'before' takes a Unix timestamp OR ISO date depending on API version;
# ISO works on the current Arctic Shift deployment.
PARAM_SETS = [
    {"subreddit": "nba", "limit": 100, "sort": "desc"},
    {"subreddit": "nba", "limit": 100, "sort": "desc", "before": "2025-01-01"},
    {"subreddit": "nba", "limit": 100, "sort": "desc", "before": "2024-06-01"},
    {"subreddit": "nba", "limit": 100, "sort": "desc", "before": "2024-01-01"},
    {"subreddit": "nba", "limit": 100, "sort": "desc", "before": "2023-06-01"},
]

# Filters to drop low-signal comments before you ever look at them.
SKIP_KEYWORDS = [
    "http://", "https://", "[deleted]", "[removed]",
    "i'm a bot", "i am a bot", "^^^", "your submission was removed",
    "RemindMe", "!remindme", "good bot", "bad bot",
]
MIN_LEN = 60      # comments shorter than this rarely carry a real take
MAX_LEN = 1200    # truncate giant copypastas

seen = set()
collected = []

for params in PARAM_SETS:
    print(f"Fetching: {params}")
    try:
        r = requests.get(BASE, headers=HEADERS, params=params, timeout=30)
    except requests.RequestException as e:
        print(f"  request failed: {e}")
        time.sleep(2)
        continue

    print(f"  status {r.status_code}")
    if r.status_code != 200:
        print(f"  error: {r.text[:200]}")
        time.sleep(2)
        continue

    comments = r.json().get("data", [])
    print(f"  got {len(comments)} comments")

    kept = 0
    for c in comments:
        body = (c.get("body") or "").strip()
        if not body:
            continue
        low = body.lower()
        if any(kw.lower() in low for kw in SKIP_KEYWORDS):
            continue
        if not (MIN_LEN <= len(body) <= MAX_LEN):
            continue
        # collapse newlines so CSV stays clean
        body = " ".join(body.split())
        if body in seen:
            continue
        seen.add(body)
        collected.append(body)
        kept += 1
    print(f"  kept {kept}")
    time.sleep(1)

with open("nba_comments_raw.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["text", "label"])   # label column left blank for you to fill
    for t in collected:
        w.writerow([t, ""])

print(f"\nDONE: {len(collected)} unique comments -> nba_comments_raw.csv")
print("Next: label these, then merge with your existing 78 to clear 200.")
