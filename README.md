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

- **Genre control**: does the Pastorals split disappear once topic/genre is regressed out
  (e.g. via LDA) before clustering?
- **Committee-effect baseline**: compare books with the *same* traditional author across
  *different* KJV committees to estimate the size of translator-introduced noise itself.
- **Cross-translation replication**: repeat the pipeline on a second public-domain
  translation (e.g. the World English Bible) — splits that reproduce across independent
  translations are stronger evidence of authorial (not translational) origin. (Partially
  addressed from the other direction: the original-language extension above tests the
  *source* text directly rather than a second translation.)
- **Feature attribution**: report which specific function words / POS patterns drive
  each separation. (Partially addressed for John vs. Revelation — see
  `docs/study_guide.md` §4 on καί/δέ frequency — but not yet done systematically for
  the other comparisons.)
- **Hebrew Torah (P vs. non-P)**: this project's Hebrew extension currently covers only
  Isaiah; replicating Koppel (2011) / Yoffe (2023, 2025)'s P-source separation directly
  on the Hebrew Pentateuch is a natural next corpus.

## Contributing

Issues and PRs are welcome, especially on the open questions above. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) for ground rules and ideas.

## License

Code: MIT (see `LICENSE`). KJV text is public domain.
