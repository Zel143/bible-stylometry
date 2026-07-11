# Contributing

This project is meant as a research artifact and an educational example of applying
stylometry / basic ML (PCA, permutation tests, SVM, Burrows' Delta) to biblical texts.
Contributions, corrections, and questions are welcome — especially from people newer
to either stylometry or ML who hit friction working through the notebooks.

## Ways to contribute

- **Bug reports**: broken notebook cells, incorrect feature extraction, statistical
  errors. Open an issue with the comparison/book involved and, if possible, the
  offending code or output.
- **Open questions**: the README's "Extensions / open questions" section lists
  follow-up analyses (genre control, committee-effect baseline, cross-translation
  replication, feature attribution, Hebrew Torah P-source split). PRs tackling any of
  these are especially welcome.
- **Documentation**: clarifications to `docs/background.md` or `docs/study_guide.md`,
  or README fixes, particularly if something wasn't clear on a first read.
- **New corpora/comparisons**: additional traditionally-disputed splits, or running
  the pipeline against another public-domain translation.

## Ground rules

- Keep `src/` functions language-agnostic where possible (see `analysis.py`) so the
  same statistical machinery works across English/Hebrew/Greek.
- Don't commit third-party corpora (`data/Bible-kjv`, `data/morphhb`, `data/Nestle1904`,
  `data/HebrewLexicon`) — they're gitignored and fetched via the `git clone` commands
  in the README's Setup section.
- If you add a result, regenerate the relevant CSV/figure in `results/` rather than
  hand-editing it.
- Cite sources for any new scholarly claims (see `docs/background.md` for the existing
  citation style).

## Getting started

Follow the Setup steps in the [README](README.md), then open
`notebooks/kjv_stylometry_project.ipynb` to see the main pipeline end to end.

For questions or discussion, open a GitHub issue.
