"""
prelabel.py
Uses Groq (llama-3.3-70b-versatile) to SUGGEST a label for each raw comment.
This is a TIME-SAVER, NOT a labeler. You MUST read and correct every row.
The assignment requires reviewing every pre-labeled example and disclosing
that you used this workflow in your README's AI usage section.

Setup:
    pip install groq python-dotenv
    # create a .env file next to this script containing:
    #   GROQ_API_KEY=your_key_here
    # (.env is gitignored so the key never reaches GitHub)
    python prelabel.py

Input:  nba_comments_raw.csv   (text, label[blank])
Output: nba_comments_prelabeled.csv  (text, label[suggested], notes)
        -> open this, fix every label, write notes on hard cases.
"""

import os
import csv
import time
from dotenv import load_dotenv
from groq import Groq

# Loads GROQ_API_KEY from a local .env file into the environment.
# The key stays out of the source code entirely.
load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

# Keep these IDENTICAL to your planning.md definitions.
LABEL_PROMPT = """You are labeling r/nba comments into exactly one category.

Categories:
- analysis: makes a structured argument backed by specific, verifiable evidence
  (stats, roster/cap details, historical comparison, tactical reasoning). The
  reasoning would stand even if you stripped out the opinion.
- hot_take: a bold, confident opinion asserted WITHOUT real supporting evidence,
  or with vague/cherry-picked evidence used decoratively. Asserts rather than argues.
- reaction: an immediate emotional response, joke, or expression of feeling about
  an event. Little to no argument.
- news: a factual report of an event, transaction, or quote, with no opinion or
  argument from the commenter (e.g. relaying a reporter's tweet or a player quote).

Output ONLY the single category name in lowercase. No other text."""

def classify(text):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": LABEL_PROMPT},
            {"role": "user", "content": text[:1500]},
        ],
        temperature=0,
        max_tokens=5,
    )
    out = resp.choices[0].message.content.strip().lower()
    valid = {"analysis", "hot_take", "reaction", "news"}
    return out if out in valid else "UNSURE"

rows = list(csv.DictReader(open("nba_comments_raw.csv", encoding="utf-8")))
out_rows = []
for i, r in enumerate(rows):
    text = r["text"].strip()
    if not text:
        continue
    try:
        label = classify(text)
    except Exception as e:
        print(f"row {i} error: {e}")
        label = "UNSURE"
        time.sleep(3)
    out_rows.append({"text": text, "label": label, "notes": ""})
    if i % 20 == 0:
        print(f"{i}/{len(rows)} done")
    time.sleep(0.4)   # stay under free-tier rate limits

with open("nba_comments_prelabeled.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["text", "label", "notes"])
    w.writeheader()
    w.writerows(out_rows)

from collections import Counter
print("\nSuggested distribution:", dict(Counter(r["label"] for r in out_rows)))
print(f"Wrote {len(out_rows)} rows -> nba_comments_prelabeled.csv")
print("NOW: open it and correct every label. Flag 3+ hard cases in 'notes'.")
