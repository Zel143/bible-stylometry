# Study Guide: Reading the Bible Before Translation

This is a reading path through the project, ordered so you meet each authorial-voice question
three times: what tradition and critical scholarship say about it (`docs/background.md`), what
the stylometric numbers actually show — first in KJV English, then **directly in the Hebrew or
Greek original** (`notebooks/kjv_stylometry_project.ipynb` and
`notebooks/original_language_stylometry.ipynb`) — and finally what the original words themselves
look like up close (`notebooks/parallel_reader.ipynb`, `src/reader.py`).

The order mirrors the README results table: **Isaiah → Pauline corpus → Hebrews → Johannine →
Petrine**.

---

## 1. Isaiah 1–39 vs 40–66

**What tradition and critical scholarship say.** Tradition holds the 8th-century prophet Isaiah
of Jerusalem wrote all 66 chapters. Since the 19th century, critical scholarship has held a
near-consensus that at least three hands are present — Proto-Isaiah (1–39), Deutero-Isaiah
(40–55, exilic), and Trito-Isaiah (56–66, postexilic) — triggered by both historical anachronism
(40–66 already presuppose the Babylonian exile and name Cyrus by name, Isa 44:28–45:1) and
stylistic difference. Radday's 1970/1973 computerized tests found the second half uses
measurably longer words (2.04 vs. 2.11 average syllables/word) and 63% more inflected nouns — though Radday himself cautioned that style differences "even if objectively established, are not author-specifying." See `docs/background.md` §"Isaiah" for the full account, including the conservative counter-argument from manuscript unity (the Great Isaiah Scroll presents 1–66 as one physical unit).

**What the stylometry shows.**

| | permutation p | 5-fold SVM accuracy | n chunks |
|---|---|---|---|
| KJV English | 0.0002 | 0.96 | 24 |
| **Hebrew original** | **0.0016** | **0.90** | 14 |

Both are strongly significant — this is the cleanest possible result: the split did not need translation to appear (it's there in the Hebrew consonantal text itself), and translation did not wash it out either. See `notebooks/original_language_stylometry.ipynb` §"Isaiah" for the PCA plot and code.

**Reading in the original.** Two things make Hebrew stylometry different from English: (1)
conjunctions, prepositions, and the definite article attach as *prefixes* to the following word rather than standing alone (e.g. "and Jerusalem" is one graphic word, וִ/ירוּשָׁלִָם) — so `src/features_hebrew.py` counts these as separate morphemes rather than whole words; (2) niqqud (vowel points) are a much later addition to the consonantal text, so word-length statistics here use the stripped consonantal form. Open `notebooks/parallel_reader.ipynb` §"Isaiah 53:5" to see a worked verse: KJV's "wounded... bruised... chastisement... stripes" mapped back to the underlying Hebrew roots (châlal "pierced/profaned", dâkâʼ "crushed", mûwçâr "discipline/correction", chabbûwrâh "stripe/bruise").

---

## 2. Pauline corpus: undisputed letters vs. the Pastorals

**What tradition and critical scholarship say.** Seven letters (Romans, 1–2 Corinthians,
Galatians, Philippians, 1 Thessalonians, Philemon) form the stable "undisputed" core. The
Pastorals (1–2 Timothy, Titus) have been doubted since Harrison (1921) counted their hapax
legomena as markedly un-Pauline — but Workman (1896), Grayston & Herdan (1959), and especially
Anthony Kenny (1986, using 99 features across the whole NT) pushed back, and two 2025 papers
(Pracht & McCauley) found **no** significant difference using discrete-distribution models over
18 discourse modes. This is the project's single most genuinely open question. See
`docs/background.md` §"Pauline corpus" for the full century of back-and-forth.

**What the stylometry shows.**

| | permutation p | n chunks |
|---|---|---|
| KJV English | 0.0084 | 24 |
| **Greek original** | **0.0034** | **20** |

Both are significant at this pipeline's feature set (function-lemma frequency + sentence/word
length) — in tension with Pracht & McCauley's 2025 null result. That's not necessarily a
contradiction: their models test 18 specific discourse-mode counts; this pipeline's ~30
function-word frequencies are a different, older-style (Kenny/Morton-like) feature set. Read
this as the same open question the literature has, now visible in the Greek rather than only in
English — not as a resolution of it.

**Reading in the original.** `notebooks/parallel_reader.ipynb` §"Romans 1:1" shows Paul's
compact, formulaic Greek opening (Παῦλος δοῦλος Χριστοῦ Ἰησοῦ, κλητὸς ἀπόστολος...) as a
baseline before comparing it to Hebrews' very different opening style below.

---

## 3. Hebrews vs. the undisputed Paulines

**What tradition and critical scholarship say.** Hebrews is internally anonymous — the "of Paul" association is traditional, not textual. Doubts are ancient: Clement of Alexandria guessed Paul wrote it in Hebrew and Luke translated it into polished Greek; Origen concluded "who wrote the epistle, in truth God knows." The author explicitly places himself among second-generation Christians who received the gospel from eyewitnesses (Heb 2:3) — directly contradicting Paul's insistence on unmediated revelation (Gal 1:12). Modern consensus: not by Paul. See `docs/background.md` §"Hebrews."

**What the stylometry shows.**

| | permutation p | 5-fold SVM accuracy | n chunks |
|---|---|---|---|
| KJV English | 0.0004 | 0.92 | 26 |
| **Greek original** | **0.0012** | **0.90** | 20 |

Strongly significant in both languages — another robust, translation-independent result. The
Burrows' Delta profile attribution in `notebooks/original_language_stylometry.ipynb` also shows
Hebrews sitting closer to its own profile than to undisputed-Paul's for several other disputed
letters (Ephesians, Colossians, 2 Thessalonians, Titus, 2 Peter) — worth reading against, not
as, a verdict on those letters' authorship.

**Reading in the original.** Hebrews opens with an elaborate, rhetorically balanced periodic
sentence (Heb 1:1-2) — a single, tightly constructed Greek sentence very unlike the short
formulaic openings Paul uses. `notebooks/parallel_reader.ipynb` §"Hebrews 1:1-2" renders it
word-by-word; compare its density of participles and subordinate clauses against Romans 1:1
above.

---

## 4. Johannine literature: Gospel of John vs. Revelation

**What tradition and critical scholarship say.** Tradition assigns the Gospel, three Epistles,
and Revelation all to the apostle John. The Gospel and 1 John share elegant, nearly error-free
Greek; Revelation's Greek is rough, heavily Semitic, with grammatical solecisms so pronounced
that Dionysius of Alexandria (3rd c., preserved in Eusebius) concluded a different "John" wrote
it — one of the oldest authorship judgments in the corpus, made centuries before any
computational method existed. See `docs/background.md` §"Johannine literature."

**What the stylometry shows.**

| | permutation p | 5-fold SVM accuracy | n chunks |
|---|---|---|---|
| KJV English | 0.0002 | 1.00 | 21 |
| **Greek original** | **0.0002** | **1.00** | 17 |

Perfect or near-perfect separation in both languages — the strongest result in the whole
project. One concrete driver is visible in the raw feature averages *before* any PCA: across
this corpus, Revelation's καί ("and") frequency runs roughly 2–3× every other NT book (a
paratactic, Hebraic-influenced style — clause after clause joined by "and" rather than
subordinated), while its δέ ("but/then") frequency sits near zero. That is Dionysius's ancient
observation, now a measurable statistic.

**Reading in the original.** `notebooks/parallel_reader.ipynb` §"John 1:1 vs Revelation 1:1"
puts the Gospel's famous periodic opening (Ἐν ἀρχῇ ἦν ὁ λόγος...) directly next to Revelation's
much plainer, list-like opening verse — read them aloud one after the other and the stylistic
gulf is audible even without Greek.

---

## 5. 1 Peter vs. 2 Peter

**What tradition and critical scholarship say.** 1 Peter is fluent, cultured Greek; 2 Peter is,
in Richard Bauckham's words, "rather like baroque art, almost vulgar in its pretentiousness and
effusiveness" — different favorite vocabulary, heavy overlap with Jude (2 Peter is generally
held to have used Jude as a source), and the weakest early manuscript attestation of any
canonical book. Acts 4:13 calls Peter "unlettered" (agrammatos); defenders point to Silvanus,
named as an amanuensis in 1 Peter 5:12, to explain the gap. See `docs/background.md` §"Petrine
letters."

**What the stylometry shows.**

| | permutation p | n chunks |
|---|---|---|
| KJV English | 0.34 (n.s.) | 3 |
| **Greek original** | **1.00 (n.s.)** | **2** |

This is the project's clearest illustration of the "short-text problem" the literature warns
about repeatedly: 2 Peter is only ~1,100 Greek words, so at 1,500-word chunking it yields a
*single* chunk — a permutation test comparing one chunk against one chunk is close to
uninformative regardless of how different the letters actually are. These two letters show the
**largest raw stylistic distance of any pair in this whole project** (centroid distance ≈11.7,
higher than Isaiah, Paul/Hebrews, or John/Revelation) yet fail to reach significance purely on
sample size — a direct demonstration of why length matters as much as the sample being compared.

**Reading in the original.** `notebooks/parallel_reader.ipynb` §"1 Peter 1:1 vs 2 Peter 1:1"
puts both openings side by side — judge Bauckham's "baroque... pretentiousness" description
against 2 Peter's actual Greek for yourself.

---

## Where the stylometric feature sets differ by language, and why

- **English** (`src/features.py`): ~100 common function words by surface spelling + sentence
  length + word length + type-token ratio.
- **Hebrew** (`src/features_hebrew.py`): function *morphemes* by lemma/Strong's-number (since
  conjunctions/prepositions/the article are prefixes, not separate words) + consonantal word
  length + type-token ratio. No sentence-length feature — WLC doesn't mark sentence boundaries
  the way English/Greek punctuation does, so verse-level chunking substitutes for it.
- **Greek** (`src/features_greek.py`): function words by *lemma* (since Greek is heavily
  inflected — the article alone has dozens of surface forms across case/number/gender) +
  sentence length (Greek NT punctuation does mark sentences) + word length + type-token ratio.

This means the three feature sets are not identical numbers on identical axes — the Hebrew and
Greek p-values are not literally the same statistical test as the English one, just the same
*kind* of test (permutation test on standardized centroid distance) applied to the
language-appropriate features. Treat the cross-language comparison tables above as "does the
signal show up at all," not as a precise effect-size comparison.
