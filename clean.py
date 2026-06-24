import csv

# Posts to skip - keywords that signal spam/irrelevant content
skip_keywords = [
    "Jersey", "Adidas", "Nike", "Fantasy Basketball", "Live Streaming",
    "I WANT YOU", "horny", "lesterslegends", "RADIOUPSS", "Air Jordan",
    "http://", "lesterslegends", "Basketball Shoes", "Jerseys and Memorabilia"
]

with open("nba_posts.csv", "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = []
    for row in reader:
        text = row["text"]
        # Skip if too short
        if len(text.strip()) < 30:
            continue
        # Skip if contains spam keywords
        if any(kw.lower() in text.lower() for kw in skip_keywords):
            continue
        rows.append(row)

with open("nba_posts_clean.csv", "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["text", "label"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Cleaned dataset: {len(rows)} posts → nba_posts_clean.csv")