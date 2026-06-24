"""
merge.py — combine your reviewed comments with the original 78 post-based rows
into one training file, and report the final label distribution.

Run after you finish label_tool.py:
    python merge.py

Inputs:
    nba_posts_labeled.csv      (your original 78: text,label)
    nba_comments_reviewed.csv  (your reviewed comments: text,label,notes)
Output:
    nba_takemeter_dataset.csv  (text,label)  <- commit THIS; train on THIS
"""

import csv
import random
from collections import Counter

def load(path):
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        t = (r.get("text") or "").strip()
        l = (r.get("label") or "").strip()
        if t and l:
            out.append((t, l))
    return out

posts = load("nba_posts_labeled.csv")
comments = load("nba_comments_corrected.csv")

# Dedup by exact text; posts win if collision (unlikely).
seen, merged = set(), []
for t, l in posts + comments:
    if t not in seen:
        seen.add(t)
        merged.append((t, l))

# Shuffle so labels aren't grouped — prevents a single-class test split / leakage.
# Fixed seed = reproducible.
random.seed(42)
random.shuffle(merged)

with open("nba_takemeter_dataset.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["text", "label"])
    w.writerows(merged)

dist = Counter(l for _, l in merged)
total = len(merged)
print(f"Merged total: {total} rows -> nba_takemeter_dataset.csv\n")
for lbl, c in dist.most_common():
    flag = "  <-- OVER 70%!" if c / total > 0.70 else ""
    print(f"  {lbl:10s} {c:4d}  ({100*c/total:4.1f}%){flag}")

print()
if total < 200:
    print(f"WARNING: only {total} rows — need 200+. Label more comments.")
elif max(dist.values()) / total > 0.70:
    print("WARNING: a label exceeds 70% — rebalance before training.")
else:
    print("OK: 200+ rows and no label over 70%. Ready for the notebook.")