"""
label_tool.py — fast interactive labeling.

Shows one comment at a time with the pre-label suggestion. You press a key to
accept it or pick a different label. Saves continuously so you can quit and
resume any time. Every decision is yours; this just removes the spreadsheet
friction.

Run:
    python label_tool.py

Input:  nba_comments_prelabeled.csv   (text, label, notes)
Output: nba_comments_reviewed.csv     (text, label, notes)  -- written as you go

Keys:
    a = analysis     h = hot_take     r = reaction     n = news
    [Enter] = accept the suggested label as-is
    x = drop this row (off-topic / noise / junk)
    ? = type a note for this row (for edge cases), then it asks for the label
    b = go back one row
    q = save and quit (resume later — already-reviewed rows are skipped)
"""

import csv
import os

IN = "nba_comments_prelabeled.csv"
OUT = "nba_comments_reviewed.csv"
LABELS = {"a": "analysis", "h": "hot_take", "r": "reaction", "n": "news"}

rows = list(csv.DictReader(open(IN, encoding="utf-8")))
for r in rows:
    r.setdefault("notes", "")

# Resume support: load any rows already reviewed.
done = {}
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT, encoding="utf-8")):
        done[r["text"].strip()] = r

def save(reviewed):
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "label", "notes"])
        w.writeheader()
        w.writerows(reviewed)

reviewed = [done[r["text"].strip()] for r in rows if r["text"].strip() in done]
queue = [r for r in rows if r["text"].strip() not in done]

print(f"{len(reviewed)} already reviewed, {len(queue)} to go.\n")

i = 0
while i < len(queue):
    r = queue[i]
    sug = r["label"].strip()
    print("=" * 70)
    print(f"[{len(reviewed)+1}/{len(rows)}]  suggestion: {sug.upper()}")
    print("-" * 70)
    print(r["text"])
    print("-" * 70)
    choice = input("a/h/r/n  Enter=accept  x=drop  ?=note  b=back  q=quit > ").strip().lower()

    if choice == "q":
        break
    if choice == "b" and reviewed:
        prev = reviewed.pop()
        queue.insert(i, next(x for x in rows if x["text"].strip() == prev["text"].strip()))
        continue
    if choice == "x":
        i += 1
        save(reviewed)
        continue
    note = r.get("notes", "")
    if choice == "?":
        note = input("note: ").strip()
        choice = input("now the label (a/h/r/n, Enter=accept) > ").strip().lower()
    if choice == "":
        label = sug
    elif choice in LABELS:
        label = LABELS[choice]
    else:
        print("  (unrecognized key, accepting suggestion)")
        label = sug

    reviewed.append({"text": r["text"].strip(), "label": label, "notes": note})
    i += 1
    save(reviewed)

save(reviewed)
from collections import Counter
print(f"\nSaved {len(reviewed)} rows -> {OUT}")
print("Distribution:", dict(Counter(x["label"] for x in reviewed)))
print("Run again any time to resume. When done, send me the file to merge.")