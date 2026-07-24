# Current Status

Snapshot of where the project stands. Update this as work progresses — it should always reflect the current state, not a history (see `decisions.md` for the log of past decisions).

_Last updated: 2026-07-20_

## Summary

Stylometric analysis testing whether authorial-voice differences known from Hebrew/Greek
biblical scholarship (Isaiah 1–39 vs 40–66, undisputed Paul vs Pastorals, Paul vs Hebrews,
John vs Revelation, 1 Peter vs 2 Peter) survive translation into the KJV, using
function-word frequencies, permutation tests, SVM cross-validation, and Burrows' Delta.
The core pipeline plus five extensions (original-language, genre control, committee
baseline, cross-translation, Torah P-source split) are all built and have produced
results. Every extension listed in the README's original "Extensions / open questions"
list is now done — the project has no outstanding open questions as of this update.

## In progress

- Nothing actively in flight. Just finished the last of the three open questions
  (Hebrew Torah P-source split) that were worked through in order this session
  (committee baseline → cross-translation replication → Torah P-source split).

## Done

- Hebrew Torah P vs non-P source split (2026-07-20): `src/features_torah.py` replicates
  the documentary-hypothesis Priestly (P) vs non-Priestly (J/E) split on Genesis/Exodus/
  Leviticus/Numbers (OSHB/WLC), at whole-chapter resolution, excluding chapters known to
  interweave sources verse-by-verse (flood narrative, Korah cycle, etc.). Result:
  p = 0.0002, SVM 5-fold accuracy 0.88 (n = 41 chunks, ~60k words) — the split reproduces
  strongly. Flagged as a first-pass, chapter-granularity replication, not verse-exact.
  Also generalized `src/features_hebrew.py`'s Isaiah-only XML parsing into a reusable
  loader for any Pentateuch book. See README's new "Hebrew Torah" section and `CHANGELOG.md`.
- Cross-translation replication (2026-07-20): `src/features_web.py` +
  `src/run_web_replication.py` rerun the five key comparisons on the World
  English Bible (independent public-domain translation, no textual/committee
  relationship to the KJV). All four KJV-significant splits reproduce at
  comparable strength (Pastorals split even sharper: p 0.008 → 0.0002);
  1–2 Peter stays non-significant in both, consistent with the known
  short-text power problem. See README's "Cross-translation replication"
  section and `CHANGELOG.md`.
- Committee-effect baseline (2026-07-20): `src/committee_baseline.py` compares
  Gospel of John (Second Oxford) vs. 1–3 John (Second Westminster) as a
  cross-committee, same-author pair, and Luke vs. Acts (both Second Oxford) as a
  same-committee control. Both separate significantly (p = 0.0002 each); Luke vs.
  Acts holding author *and* committee constant still shows a real split (centroid
  distance 6.55, SVM acc 0.82), giving a noise floor to read the rest of the
  project's splits against. The cross-committee pair separates more (centroid
  distance 10.08), consistent with an added committee effect, but genre and
  sample-size imbalance aren't cleanly isolated in this design — flagged as a
  first pass. See README's "Committee-effect baseline" section and `CHANGELOG.md`.
- Core KJV pipeline: corpus chunking, ~100 function-word features, PCA, permutation
  test, 5-fold linear-SVM CV, Burrows' Delta (`src/features.py`, `src/analysis.py`,
  `notebooks/kjv_stylometry_project.ipynb`).
- All five key comparisons run, with 4 of 5 splits statistically significant
  (Isaiah, Paul-vs-Pastorals, Paul-vs-Hebrews, John-vs-Revelation); 1–2 Peter is
  not significant, attributed to short-text size (2 Peter ≈1,100 words).
- Original-language extension: same tests rerun directly on Hebrew (Isaiah, via
  OSHB/WLC) and Greek (Nestle 1904) — same four splits reproduce in the source
  language, confirming the signal isn't a translation artifact
  (`src/features_hebrew.py`, `src/features_greek.py`, `src/run_original_language_analysis.py`,
  `notebooks/original_language_stylometry.ipynb`).
- Genre control extension (2026-07-11): LDA topic residualization to check whether
  the Pastorals split is genre rather than authorship. Result: Pastorals split
  *sharpens* under genre control (p 0.0084 → 0.0008); Paul-vs-Hebrews *weakens*
  (p 0.0004 → 0.094, n.s.) since Hebrews' priesthood/tabernacle topic explains
  some of its apparent distinctiveness (`src/genre_control.py`, see `CHANGELOG.md`).
- Feature attribution: SVM feature weights ranked per comparison
  (`results/feature_weights_*.csv`), so results aren't just a black-box score.
- Parallel reader tool for close reading (original + transliteration + gloss +
  KJV + optional ESV) (`src/reader.py`, `notebooks/parallel_reader.ipynb`).
- Docs: README with full write-up and key-results tables, `docs/background.md`
  (literature review), `docs/study_guide.md` (guided reading path), `CONTRIBUTING.md`,
  `CHANGELOG.md`.

## Open questions / blockers

- No open extensions remain from the README's original list. Two known caveats worth
  revisiting if this project continues:
  - The committee-effect baseline design doesn't cleanly separate "committee effect" from
    genre/sample-size confounds — a cleaner isolation would need a same-author pair
    matched on genre across committees, if one can be found.
  - The Torah P-source split uses whole-chapter resolution and excludes interwoven
    chapters (flood narrative, Korah cycle, etc.) rather than a verse-exact source
    division (e.g. Friedman 2003) — a finer-grained version would need verse-level
    chunking infrastructure this project doesn't currently have.

## Next up

- No specific extension queued. Possible directions if resuming: verse-level chunking
  infrastructure (would unlock a finer-grained Torah split), or a genuinely
  genre-matched committee-effect pair if one can be identified.
