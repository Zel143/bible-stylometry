# Changelog

Notable extensions and experiments run on this project, newest first. Follows
[Keep a Changelog](https://keepachangelog.com) conventions loosely: each entry
says what was tested and what was found, not just what code changed (see git
history for that).

## 2026-07-20 — Committee-effect baseline

Added `src/committee_baseline.py` to estimate how much stylistic noise a KJV
translation company introduces on its own, per the README's "Extensions /
open questions" list. Added `1John`, `2John`, `3John`, `Luke`, `Acts` to
`src/features.py`'s `BOOKS` metadata to support it.

Method: compare two same-traditional-author pairs. Gospel of John (Second
Oxford company) vs. 1–3 John (Second Westminster company) isolates a
cross-committee, same-author case — chosen over Gospel of John vs. Revelation
(already tested elsewhere as an authorship split) because 1 John is the
Johannine-corpus text stylistically closest to the Gospel, and its
authorship is far less contested. Luke vs. Acts (both Second Oxford) is the
same-committee control.

**Findings**:
- Both pairs separate significantly: John vs 1–3 John, p = 0.0002, centroid
  distance 10.08 (n = 17 chunks, 13 gospel / 4 epistle — too few epistle
  chunks for 5-fold CV). Luke vs Acts, p = 0.0002, centroid distance 6.55,
  SVM 5-fold accuracy 0.82 (n = 33 chunks).
- Luke vs Acts holding *both* author and committee constant still separates
  significantly — this pipeline's function-word features pick up a real,
  measurable split even in the best-case "no confound" scenario, most likely
  from genre/source-material differences between the two halves of a single
  two-volume history. That's a useful noise floor for reading the rest of
  this project's splits against.
- The cross-committee pair's larger centroid distance (10.08 vs 6.55) is
  consistent with an added committee effect, but genre (gospel vs. epistle)
  and sample-size imbalance aren't cleanly separated out in this design —
  flagged as a first pass, not a clean isolation of the committee variable.

Outputs: `results/committee_baseline_results.csv`,
`results/feature_weights_johannine_committee.csv`,
`results/figures/fig5_johannine_committee.png`,
`results/figures/fig6_lukan_committee.png`. Written up in the README's new
"Committee-effect baseline" section.

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
