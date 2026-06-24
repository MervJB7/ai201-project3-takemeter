# TakeMeter — Planning Document

## Community

I chose **r/nba**, the main NBA discussion subreddit. It's a strong fit for a
discourse-quality classifier because the same news event produces wildly
different kinds of posts: a reporter's trade tweet, a stat-backed breakdown of
how that trade reshapes a roster, a confident "this team just won the
championship" assertion with no support, and a one-line joke or emotional
reaction. That natural variety in *how* people talk about the same topics is
exactly the signal a classifier needs. The content is public, text-heavy, and
high-volume, so collecting 200+ examples is feasible.

## Labels

I use a **4-label taxonomy**. Each post is assigned exactly one label.

- **analysis** — The comment makes a structured argument backed by specific,
  verifiable evidence: stats, roster/salary-cap details, historical comparison,
  or tactical reasoning. The reasoning would still stand if you removed the
  opinion framing.
  - *Example:* "MKE wants picks, Boston's best asset is Jaylen Brown and the
    Heat's best asset is this year's #13... both the Celtics and Heat get better
    if they acquire Giannis and Brown respectively, and MKE could come back with
    #13, #27 and solid pieces."
  - *Example:* "The Giannis saga is overshadowing that this is our first look at
    a rebuild under the new draft-lottery rules. Before, the expected package for
    a superstar request was predictable; now the math changes how teams value
    picks."

- **hot_take** — A bold, confident opinion asserted *without* real supporting
  evidence, or with vague/cherry-picked evidence used decoratively. It asserts
  rather than argues.
  - *Example:* "Loyalty from a player is the most overrated thing in sports. Do
    what's best for yourself."
  - *Example:* "Bam and Giannis is the best duo since healthy LeBron and AD —
    cmon, the East is going to be BRUTAL next year."

- **reaction** — An immediate emotional response, joke, or expression of feeling
  about an event. Little to no argument.
  - *Example:* "The Heat and Celtics have the potential to do the funniest thing
    ever — just take the Giannis packages from both teams and trade with each
    other."
  - *Example:* "Jaylen Brown: to all the people that doubted me, you're turning
    me into a monster."

- **news** — A factual report of an event, transaction, or quote, with no opinion
  or argument from the poster (typically relaying a reporter's tweet).
  - *Example:* "[Charania] The Heat and Celtics are the only two teams in the
    Giannis sweepstakes that have gotten his commitment to sign long term."
  - *Example:* "[Fischer] Darryn Peterson told me at media day he met with the
    Jazz this weekend — more of a Combine-like interview than on-court."

**Why these distinctions matter to r/nba:** Regulars constantly police the
difference between a "hot take" and "actual analysis" — it's native vocabulary in
the community. Separating both from raw reaction and from reposted news reflects
how the subreddit itself talks about post quality.

## Hard edge cases

The boundaries that genuinely blur during annotation:

1. **hot_take vs. analysis** — a comment that cites *one* stat but uses it
   decoratively. **Decision rule:** if the evidence is specific and would support
   the claim even with the opinion stripped out → analysis. If it's vague,
   cherry-picked, or just enough to sound credible → hot_take.

2. **news vs. reaction** — a reported player quote (e.g. Jaylen Brown's "you're
   turning me into a monster"). It's a quote (news-like) but it's emotional
   content, not a transaction report. **Decision rule:** if the *commenter* is
   neutrally relaying a fact/transaction → news; if the comment IS the emotional
   content or the poster reacts to it → reaction.

3. **news vs. analysis** — a trade-rumor post that reports the rumor *and* adds
   reasoning about why it makes sense. **Decision rule:** if the post is mostly
   relaying → news; if it adds non-trivial argument the reporter didn't → analysis.

(At least 3 specific real examples encountered during annotation are recorded in
the dataset's `notes` column and summarized here as I label.)

## Data collection plan

- **Source:** public r/nba comments via the Arctic Shift API (`scrape_comments.py`),
  supplemented by the initial 78 post-based examples already labeled.
- **Target:** 200+ total, aiming for at least ~20% per label (≈40+ each).
- **Underrepresented labels:** `reaction` is the thinnest class so far. If any
  label sits below ~20% after the first pass, I pull additional targeted comments
  (e.g. game-thread comments skew toward reaction) and label more of that class
  rather than accepting imbalance.

## Evaluation metrics

- **Overall accuracy** — headline number, but insufficient alone because the
  classes aren't perfectly balanced; accuracy can hide a class the model ignores.
- **Per-class precision / recall / F1** — the real test. I care most about whether
  the model can hold the **analysis vs. hot_take** boundary, since that's the
  subjective, community-meaningful distinction. Low F1 on either reveals the model
  collapsed them.
- **Confusion matrix** — to see the *direction* of errors (e.g. analysis → hot_take
  specifically), which tells me which boundary failed.

## Definition of success

- **Minimum bar:** fine-tuned model beats the zero-shot Groq baseline on overall
  accuracy, and no single class has F1 ≈ 0 (i.e. it learns every label at least
  somewhat).
- **Genuinely useful:** all four per-class F1 ≥ 0.65, with the analysis/hot_take
  pair distinguished better than chance. That would make it usable as a
  rough "take-quality" tagger for a community tool.
- **Honest expectation:** analysis vs. hot_take is subjective and 200 examples is
  small, so I expect this to be the weakest boundary and will report it plainly.

## AI Tool Plan

- **Label stress-testing:** Before annotating at scale, I fed my label definitions
  and edge-case rules to an LLM and asked it to generate boundary posts. Where it
  produced comments I couldn't classify cleanly, I tightened the definitions
  (notably the hot_take vs. analysis "evidence would stand alone" rule).
- **Annotation assistance:** I use `prelabel.py` (Groq llama-3.3-70b-versatile) to
  pre-suggest a label for each scraped comment, then **review and correct every
  row** by hand. Pre-labeled rows are tracked via the file they came from and
  disclosed in the README's AI usage section.
- **Failure analysis:** After fine-tuning, I'll paste the list of misclassified
  test examples into an LLM, ask it to surface patterns (label pair confused,
  short posts, sarcasm), then verify each pattern myself against the actual
  examples before writing it up.
