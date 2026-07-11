# Changelog

Notable extensions and experiments run on this project, newest first. Follows
[Keep a Changelog](https://keepachangelog.com) conventions loosely: each entry
says what was tested and what was found, not just what code changed (see git
history for that).

## 2026-07-11 — Genre control (LDA topic residualization)

Added `src/genre_control.py` to test whether the Pastorals-vs-undisputed-Paul
split is genre (church-organization vocabulary) rather than authorship, per
the README's "Extensions / open questions" list.

Method: fit a 6-topic LDA on content words (function words excluded) across
the Pauline corpus + Hebrews, residualize every style feature (function-word
frequencies, sentence/word stats) against each chunk's topic proportions via
OLS, then rerun the permutation test on the residuals. Hebrews-vs-undisputed
included as a same-corpus control, since it's already a robust split.

**Findings**:
- Undisputed vs Pastorals: p went from 0.0084 (raw) to 0.0008 (topic-residualized)
  — the split *sharpens* under genre control, arguing against a pure
  vocabulary/genre explanation.
- Undisputed vs Hebrews: p went from 0.0004 (raw) to 0.094, n.s.
  (topic-residualized) — this split partly *weakens*, since LDA topic 5
  (`priest, high, day, angels, house, enter`) captures Hebrews' priesthood/
  tabernacle content directly, and controlling for it removes some of what
  looked like authorial signal.

Outputs: `results/genre_control_results.csv`, `results/genre_control_topics.csv`,
`results/figures/fig4_genre_raw.png`, `results/figures/fig4_genre_residualized.png`.
Written up in the README's new "Genre control" section.
