# Stylometric Fingerprints Across Translation

**Do authorial-voice differences detected in the original Hebrew/Greek survive translation into the King James Version?**

A century of stylometric research on the Hebrew/Greek biblical texts finds a consistent
pattern: certain traditionally-grouped texts (Isaiah 1–39 vs. 40–66; the seven "undisputed"
Pauline letters vs. the Pastorals; Hebrews vs. Paul; Revelation vs. the Gospel of John;
1 Peter vs. 2 Peter) show measurable stylistic separation in the source languages — with
some splits robust (Isaiah, Hebrews, Johannine corpus) and others genuinely contested in
recent literature (the Pastorals).

This project asks: **does that signal survive translation into English**, or is it
overwritten by the KJV translators' own house style? The KJV was produced by six
separate committees, each with its own assigned books — so any English-level style
difference *within* a single committee's assigned block cannot be a translation artifact.

## In plain English

Everyone has their own way of talking — favorite little words, sentence habits — even
when they're not trying to. This project checks whether biblical texts that are
*supposed* to be written by the same person actually sound like it, by counting how
often each text uses small, forgettable words ("the," "and," "thy," "unto") rather than
what it's about.

The catch: the Bible most people read (the KJV) is a translation, made centuries ago by
several different teams. So if two "same author" texts sound different, is that the
original writer, or just a translator's habit? This project checks pairs where we
*know* the same translation team did both halves — so if a style difference shows up
anyway, it can't be blamed on the translators. It also checks the original Hebrew and
Greek directly, and teaches a computer to try to tell the styles apart (that's the
machine-learning piece), with a statistical test for whether its "guess" could just be
luck. Finally, it asks the computer *which specific words* gave it away, instead of
just reporting a confidence score — e.g. "this half uses 'thy' three times more than
the other half."

## Key results

| Comparison | Same KJV committee? | Permutation p | 5-fold SVM accuracy |
|---|---|---|---|
| Isaiah 1–39 vs 40–66 | Yes (First Oxford) | 0.0002 | 0.96 |
| Undisputed Paul vs Pastorals | Yes (Second Westminster) | 0.008 | — |
| Undisputed Paul vs Hebrews | Yes (Second Westminster) | 0.0004 | 0.92 |
| Gospel of John vs Revelation | Yes (Second Oxford) | 0.0002 | 1.00 |
| 1 Peter vs 2 Peter | Yes (Second Westminster) | 0.34 (n.s., only 3 chunks) | — |

**Takeaways:**
- Isaiah's split, Hebrews' distinctiveness, and the John/Revelation gulf all reproduce
  strongly in English, and cannot be committee artifacts since one company translated
  each pair.
- The Pastorals separate weakly in English even though recent Greek studies (Pracht &
  McCauley 2025) found no significant split — a candidate genre or translation artifact,
  flagged here as an open question rather than resolved.
- 1–2 Peter show the largest raw stylistic distance of any pair but fail to reach
  significance — a direct illustration of the "short text" problem the literature warns
  about (2 Peter is only ~1,100 words).

See [`notebooks/kjv_stylometry_project.ipynb`](notebooks/kjv_stylometry_project.ipynb)
for the full analysis, figures, and discussion.

## Original-language extension

The tests above all run on the KJV *translation*. A second pipeline runs the same permutation
test / SVM / Burrows' Delta machinery **directly on the Hebrew and Greek originals** — Isaiah via
the Westminster Leningrad Codex ([openscriptures/morphhb](https://github.com/openscriptures/morphhb))
and the Pauline/Hebrews/Johannine/Petrine comparisons via the Nestle 1904 Greek text
([biblicalhumanities/Nestle1904](https://github.com/biblicalhumanities/Nestle1904)) — to check
whether the signal needed translation to appear at all:

| Comparison | KJV English p | Original-language p |
|---|---|---|
| Isaiah 1–39 vs 40–66 | 0.0002 | 0.0016 (Hebrew) |
| Undisputed Paul vs Pastorals | 0.008 | 0.0034 (Greek) |
| Undisputed Paul vs Hebrews | 0.0004 | 0.0012 (Greek) |
| Gospel of John vs Revelation | 0.0002 | 0.0002 (Greek) |
| 1 Peter vs 2 Peter | 0.34 (n.s.) | 1.0 (n.s., only 2 chunks) |

Isaiah, Hebrews, and John/Revelation all reproduce strongly in the original language too — the
splits were never purely a translation-visible phenomenon. See
[`notebooks/original_language_stylometry.ipynb`](notebooks/original_language_stylometry.ipynb)
for the full run, and [`docs/study_guide.md`](docs/study_guide.md) for a guided reading path
that pairs each result with the underlying scholarly debate (`docs/background.md`) and the
original words themselves.

## Cross-translation replication

All results above run on the KJV. If a split is authorial rather than a KJV-specific
translation artifact, it should also show up in an independently-produced translation.
The same five comparisons were rerun on the **World English Bible**
([TehShrike/world-english-bible](https://github.com/TehShrike/world-english-bible)), a
public-domain modern-English translation with no textual or committee relationship to
the KJV:

| Comparison | KJV p | WEB p | KJV SVM acc | WEB SVM acc |
|---|---|---|---|---|
| Isaiah 1–39 vs 40–66 | 0.0002 | 0.0002 | 0.96 | 0.95 |
| Undisputed Paul vs Pastorals | 0.008 | 0.0002 | — | — |
| Undisputed Paul vs Hebrews | 0.0004 | 0.0004 | 0.92 | 0.93 |
| Gospel of John vs Revelation | 0.0002 | 0.0002 | 1.00 | 1.00 |
| 1 Peter vs 2 Peter | 0.34 (n.s.) | 0.67 (n.s.) | — | — |

All four significant KJV splits reproduce in the WEB at essentially the same strength
(the Pastorals split is even sharper in the WEB), and 1–2 Peter fails to reach
significance in both, for the same reason: too little text (2 Peter is ~1,100 words in
either translation, well under the chunk size). Since the WEB shares no translation
committee or textual lineage with the KJV, this is independent evidence that the splits
track authorial style rather than a quirk of one 17th-century translation team. See
`src/features_web.py`, `src/run_web_replication.py`, `results/web_replication_results.csv`,
and `results/figures/web_fig1_isaiah.png` / `web_fig2_paul.png` / `web_fig3_john.png`.

## Genre control

Does the Pastorals split disappear once topic/subject matter is regressed out? An LDA
topic model (6 topics, content words only — function words excluded) is fit on the
Pauline corpus + Hebrews; each chunk's style features (function words, sentence/word
stats) are then residualized against its topic proportions via OLS before rerunning the
permutation test. Hebrews vs. undisputed Paul is included as a same-corpus control,
since it's already a robust, uncontested split (see Key results above) — if genre
control collapsed that split too, that would suggest the control was destroying real
authorial signal rather than isolating genre confound.

| Comparison | Raw p | Topic-residualized p |
|---|---|---|
| Undisputed Paul vs Pastorals | 0.0084 | **0.0008** (stronger) |
| Undisputed Paul vs Hebrews | 0.0004 | 0.094 (n.s.) |

The Pastorals split does *not* collapse under genre control — it sharpens, arguing
against a pure "church-organization vocabulary" explanation. Hebrews' split, by
contrast, weakens substantially: LDA topic 5 (`priest, high, day, angels, house, enter`)
captures Hebrews' priesthood/tabernacle subject matter directly, and controlling for it
removes a meaningful share of what looked like authorial signal — a useful caveat on
how "robust" that split really is. See `src/genre_control.py`,
`results/genre_control_results.csv`, and `results/genre_control_topics.csv` (topic-word
lists) for the full run, and `results/figures/fig4_genre_raw.png` /
`fig4_genre_residualized.png` for the before/after PCA plots.

## Committee-effect baseline

The rest of this project argues that a same-committee stylistic split can't be a
translation artifact, since one company translated both halves. But how much
stylistic noise does a company introduce on its own? Two same-traditional-author
pairs isolate that:

| Comparison | Same KJV committee? | Permutation p | 5-fold SVM accuracy |
|---|---|---|---|
| Gospel of John vs 1–3 John | No (2nd Oxford vs 2nd Westminster) | 0.0002 | — (4 epistle chunks, below fold count) |
| Luke vs Acts | Yes (2nd Oxford, both) | 0.0002 | 0.82 |

Both pairs separate significantly — including Luke vs Acts, where committee *and*
traditional author are both held constant. That's the useful finding: even in the
best case for "no confound," this pipeline's function-word features still pick up
a real, measurable split, most plausibly from genre/source-material differences
between a two-volume history's two halves rather than the committee itself. That
sets a noise floor to read the rest of this project's splits against.

The cross-committee pair (John vs 1–3 John) separates by a wider margin (centroid
distance 10.08 vs 6.55) than the same-committee control, consistent with a
translation-company effect adding to the gap — though the two pairs differ in genre
(gospel narrative vs. epistle) and sample size (13 gospel chunks vs. only 4 across
the three short epistles) in ways this design doesn't fully separate from a pure
committee effect. Treat this as a first pass rather than a clean isolation of the
committee variable. See `src/committee_baseline.py`,
`results/committee_baseline_results.csv`, and `results/figures/fig5_johannine_committee.png`
/ `fig6_lukan_committee.png`.

There's also a verse-by-verse **parallel reader**
([`notebooks/parallel_reader.ipynb`](notebooks/parallel_reader.ipynb), `src/reader.py`) for
close reading: original word + transliteration + gloss, next to the full KJV verse and (with
your own free key from [api.esv.org](https://api.esv.org), set as `ESV_API_KEY`) the full ESV
verse.

## Method

1. **Corpus**: KJV text (public domain), chunked into ~1,500-word segments per book
   (or per traditionally-disputed section, e.g. Isaiah 1–39 vs 40–66).
2. **Features**: ~100 function-word relative frequencies (topic-robust style markers),
   plus average/std sentence length, average word length, and type-token ratio.
3. **Statistics**:
   - PCA for visualization
   - A permutation test on standardized group-centroid distance (distribution-free,
     appropriate for small ancient-text corpora)
   - Linear-SVM 5-fold cross-validation for held-out separability
   - Burrows' Delta to attribute each disputed letter to its nearest stylistic profile

## Repo structure

```
src/features.py                     # KJV English: corpus loading, chunking, feature extraction
src/features_hebrew.py              # Hebrew Isaiah: same, via OSHB/WLC morphology
src/features_greek.py               # Greek NT: same, via Nestle 1904 morphology
src/chunking.py                     # shared word-count chunking helper
src/analysis.py                     # PCA, permutation tests, SVM CV, Burrows' Delta (language-agnostic)
src/run_original_language_analysis.py  # runs analysis.py's tests on Hebrew/Greek
src/genre_control.py                # LDA topic model + residualization (genre-control extension)
src/committee_baseline.py           # same-author, cross- vs same-committee pairs (noise-floor extension)
src/features_web.py                 # World English Bible: corpus loading, chunking (cross-translation extension)
src/run_web_replication.py          # runs analysis.py's tests on the WEB
src/reader.py                       # verse-by-verse parallel reader (original + KJV + ESV)
notebooks/                           # the full annotated analyses (start here)
docs/study_guide.md                  # guided reading path: tradition, stylometry, original text
results/                             # output CSVs and figures from a full run
data/                                # not tracked — see setup below
```

## Setup

```bash
git clone https://github.com/aruljohn/Bible-kjv.git data/Bible-kjv
git clone https://github.com/openscriptures/morphhb.git data/morphhb
git clone https://github.com/biblicalhumanities/Nestle1904.git data/Nestle1904
git clone https://github.com/openscriptures/HebrewLexicon.git data/HebrewLexicon
git clone https://github.com/TehShrike/world-english-bible.git data/WEB
pip install -r requirements.txt
jupyter notebook notebooks/kjv_stylometry_project.ipynb
```

Optional, for the ESV column in the parallel reader: sign up for a free API key at
[api.esv.org](https://api.esv.org) and `export ESV_API_KEY=...` before running
`notebooks/parallel_reader.ipynb`.

## Background reading

This project builds on a literature review of stylometric authorship studies on the
Hebrew/Greek biblical texts, covering Radday & Shore (1985), Koppel et al. (2011),
Yoffe et al. (2023, 2025), Kenny (1986), Savoy (2019), and Pracht & McCauley (2025).
See [`docs/background.md`](docs/background.md).

## Extensions / open questions

- ~~**Genre control**~~: done — see the "Genre control" section above. The Pastorals
  split survives (and sharpens) once LDA topic is regressed out; Hebrews' split partly
  weakens, since some of its distinctiveness is topically (priesthood) driven.
- ~~**Committee-effect baseline**~~: done — see the "Committee-effect baseline" section
  above. Both a cross-committee pair (John vs 1–3 John) and a same-committee control
  (Luke vs Acts) separate significantly, giving a noise floor to read the rest of this
  project's splits against, though the design doesn't fully isolate committee from genre.
- ~~**Cross-translation replication**~~: done — see the "Cross-translation replication"
  section above. All four significant KJV splits reproduce in the World English Bible at
  comparable strength; 1–2 Peter stays non-significant in both, consistent with a
  short-text power problem rather than a KJV-specific artifact.
- ~~**Feature attribution**~~: done — `src/analysis.py`'s `svm_feature_weights()` ranks
  each comparison's function words by SVM weight (`results/feature_weights_*.csv`,
  with plots and interpretation in `notebooks/kjv_stylometry_project.ipynb`). See also
  `docs/study_guide.md` §4 on καί/δέ frequency for John vs. Revelation specifically.
- **Hebrew Torah (P vs. non-P)**: this project's Hebrew extension currently covers only
  Isaiah; replicating Koppel (2011) / Yoffe (2023, 2025)'s P-source separation directly
  on the Hebrew Pentateuch is a natural next corpus.

### Non-goals

- **Translation accuracy/quality.** This project asks whether an *authorial* stylistic
  signal survives translation — it does not attempt to judge how faithful or "accurate"
  any translation (KJV or otherwise) is to the source text. That's a different research
  question (translation-quality assessment: semantic alignment to the original,
  reference-based scoring, human judgment) requiring different methodology than the
  function-word stylometry used here, and it's out of scope for this repo.

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for a running log of extensions and experiments
(what was tested, what was found), newest first.

## Contributing

Issues and PRs are welcome, especially on the open questions above. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) for ground rules and ideas.

## License

Code: MIT (see `LICENSE`). KJV text is public domain.
