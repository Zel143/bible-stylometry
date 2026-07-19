# Decision Log

Running log of notable decisions made on this project — what was decided, why, and what alternatives were considered. Newest entries at the top.

---

## 2026-07-20 — Torah P vs non-P split: whole-chapter resolution, excluding interwoven chapters

**Decision:** Replicated the documentary-hypothesis P-vs-J/E split using whole-chapter
inclusion/exclusion rather than verse-level source attribution, and deliberately excluded
chapters known to interweave P and J/E material (Genesis 6–9, 10–11; Exodus 6–7, 12;
Numbers 16–17, 20) from both groups rather than assigning them a whole-chapter label.

**Why:** This project's existing chunking machinery (`chunk_by_wordcount` /
`chapter_filter`) only filters by whole chapter number, inherited from how the Isaiah
1–39-vs-40–66 split already works — adding verse-level filtering would be a bigger,
separate piece of infrastructure work. Guessing a whole-chapter label for a chapter
that scholarship agrees is genuinely mixed (e.g. the flood narrative) would manufacture
signal rather than measure it, so those chapters were left out entirely instead.

**Alternatives considered:** Verse-level source attribution (e.g. reproducing Friedman's
2003 "The Bible with Sources Revealed" division exactly) — rejected for this pass as
disproportionate infrastructure work relative to the rest of this project's chapter-level
conventions; flagged in the README/CHANGELOG as a coarser, first-pass replication rather
than a verse-exact one, leaving the finer-grained version as a possible future extension.

---

## 2026-07-20 — Committee-effect baseline: chose John vs 1–3 John over John vs Revelation

**Decision:** Built the committee-effect baseline extension around Gospel of John (Second
Oxford) vs. 1–3 John (Second Westminster) as the cross-committee, same-author pair, plus
Luke vs. Acts (both Second Oxford) as the same-committee control.

**Why:** John vs. Revelation was the obvious cross-committee, same-traditional-author
candidate at first glance, but Revelation's Johannine authorship is genuinely contested in
NT scholarship and it's already used elsewhere in this project as an authorship-split test
case — using it again here would confound "committee effect" with "real/disputed authorship
difference." 1 John is the Johannine-corpus text stylistically closest to the Gospel and its
authorship is far less contested, making it a cleaner same-author assumption.

**Alternatives considered:** John vs. Revelation (rejected: confounds committee effect with
disputed authorship, and double-dips a comparison already used for a different purpose).
Solomon's or Moses' traditional corpora (rejected: books traditionally attributed to Solomon
or the Pentateuch to Moses all fall inside a single KJV company each, so there's no
cross-committee split available for either).

---

## 2026-07-20 — Added `docs/context/` for decision log and status tracking

**Decision:** Track decision logs and current status in `docs/context/` alongside existing `docs/background.md` and `docs/study_guide.md`, rather than in the outer `.claude` wrapper folder.

**Why:** This content should be version-controlled with the code it explains, and `docs/` was already the established location for project documentation.

**Alternatives considered:** Storing context files outside the git repo (in the wrapper folder) — rejected because it wouldn't be tracked in history alongside the code changes it documents.

---

<!--
Template for new entries:

## YYYY-MM-DD — Short title

**Decision:** What was decided.

**Why:** The reasoning or constraint that drove it.

**Alternatives considered:** What else was on the table and why it was passed over.
-->
