# Current Status

Snapshot of where the project stands. Update this as work progresses — it should always reflect the current state, not a history (see `decisions.md` for the log of past decisions).

_Last updated: 2026-07-20_

## Summary

Stylometric analysis testing whether authorial-voice differences known from Hebrew/Greek
biblical scholarship (Isaiah 1–39 vs 40–66, undisputed Paul vs Pastorals, Paul vs Hebrews,
John vs Revelation, 1 Peter vs 2 Peter) survive translation into the KJV, using
function-word frequencies, permutation tests, SVM cross-validation, and Burrows' Delta.
The core pipeline, the original-language (Hebrew/Greek) extension, and a genre-control
extension are all built and have produced results. The project is in a mature, working
state — currently between extensions, with a few open questions still unaddressed.

## In progress

- Nothing actively in flight. Just finished the committee-effect baseline extension
  and pushed all outstanding local commits to `origin/main`.

## Done

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

- **Cross-translation replication** not yet done: rerunning the pipeline on a second
  public-domain translation (e.g. World English Bible) to check whether splits
  reproduce independent of the KJV specifically. Partially covered already by the
  original-language extension, but not from the "second translation" angle.
- **Hebrew Torah (P vs. non-P) source split** not yet replicated: the Hebrew extension
  currently only covers Isaiah; extending to the Pentateuch (per Koppel 2011 / Yoffe
  2023, 2025) is a natural next corpus but unstarted.
- The committee-effect baseline design doesn't cleanly separate "committee effect" from
  genre/sample-size confounds (see Done entry above) — a cleaner isolation would need a
  same-author pair matched on genre across committees, if one can be found.

## Next up

- Pick the next open extension: cross-translation replication (WEB) or the Hebrew
  Torah P-source split.
