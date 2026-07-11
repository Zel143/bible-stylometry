"""
Greek Stylometry Pipeline
Loads the Greek New Testament (Nestle 1904 critical text, morphologically
tagged by biblicalhumanities.org), chunks it per book, and extracts
stylometric features analogous to features.py's English pipeline.

Function-word frequency is computed on the *lemma* field rather than
surface spelling, since Greek is highly inflected (e.g. the article ὁ/ἡ/τό
takes dozens of surface forms across case/number/gender but is one lemma)
— matching against inflected surface forms would undercount these words
and wash out the very signal (Kenny 1986, Morton) this pipeline is testing.
"""
import os, re, csv, unicodedata
import numpy as np
import pandas as pd
from chunking import chunk_by_wordcount

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NESTLE_DIR = os.environ.get("NESTLE1904_DIR", os.path.join(REPO_ROOT, "data", "Nestle1904"))
MORPH_CSV = os.path.join(NESTLE_DIR, "morph", "Nestle1904.csv")

# High-frequency, topic-robust closed-class Greek lemmas (Kenny 1986; Morton).
GREEK_FUNCTION_LEMMAS = [
    "ὁ", "καί", "αὐτός", "σύ", "δέ", "ἐν", "ἐγώ", "εἰμί", "εἰς", "οὐ", "ὅς",
    "οὗτος", "ὅτι", "πᾶς", "μή", "γάρ", "ἐκ", "ἐπί", "πρός", "ἵνα", "διά",
    "ἀπό", "ἀλλά", "τε", "ὡς", "κατά", "μετά", "ὑπό", "τίς", "οὖν", "εἰ",
]

GREEK_LETTER_RE = re.compile(r"[Ͱ-Ͽἀ-῿]+")

# OSIS-style book id -> (traditional author, critical grouping), mirroring
# features.py:BOOKS so KJV-English and Greek-original results are directly
# comparable side by side.
BOOKS_GREEK = {
    "Rom":     ("Paul", "undisputed"),
    "1Cor":    ("Paul", "undisputed"),
    "2Cor":    ("Paul", "undisputed"),
    "Gal":     ("Paul", "undisputed"),
    "Phil":    ("Paul", "undisputed"),
    "1Thess":  ("Paul", "undisputed"),
    "Phlm":    ("Paul", "undisputed"),
    "Eph":     ("Paul", "disputed_deutero"),
    "Col":     ("Paul", "disputed_deutero"),
    "2Thess":  ("Paul", "disputed_deutero"),
    "1Tim":    ("Paul", "pastoral"),
    "2Tim":    ("Paul", "pastoral"),
    "Titus":   ("Paul", "pastoral"),
    "Heb":     ("Paul(trad)", "non_pauline"),
    "1Pet":    ("Peter", "petrine_1"),
    "2Pet":    ("Peter", "petrine_2"),
    "John":    ("John", "johannine_gospel"),
    "Rev":     ("John", "johannine_apoc"),
}


def _load_all_verses():
    """Parse Nestle1904.csv once; return {book: [(chapter, verse, [(surface, lemma), ...])]}."""
    books = {}
    with open(MORPH_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            book_ref, cv = row["BCV"].rsplit(" ", 1)
            chapter, verse = cv.split(":")
            key = (int(chapter), int(verse))
            surface = unicodedata.normalize("NFC", row["text"])
            lemma = unicodedata.normalize("NFC", row["lemma"])
            verses = books.setdefault(book_ref, {})
            verses.setdefault(key, []).append((surface, lemma))
    return {b: [(c, v, w) for (c, v), w in sorted(vs.items())] for b, vs in books.items()}


_ALL_VERSES = None


def load_book(book_id):
    """Return list of (chapter:int, verse_text:str) tuples for one OSIS book id.

    verse_text is a space-joined string of "surface|lemma" tokens (one per
    original word), so downstream chunking counts real words while keeping
    the lemma needed for function-word frequency.
    """
    global _ALL_VERSES
    if _ALL_VERSES is None:
        _ALL_VERSES = _load_all_verses()
    out = []
    for chapter, _verse, words in _ALL_VERSES[book_id]:
        tokens = [f"{s}|{l}" for s, l in words]
        out.append((chapter, " ".join(tokens)))
    return out


def get_verse_words(book_id, chapter, verse):
    """Return [(surface, lemma), ...] for one verse, or [] if not found."""
    global _ALL_VERSES
    if _ALL_VERSES is None:
        _ALL_VERSES = _load_all_verses()
    for c, v, words in _ALL_VERSES.get(book_id, []):
        if c == chapter and v == verse:
            return words
    return []


def chunk_book(book_id, chapter_filter=None, chunk_words=1500, label=None):
    verses = load_book(book_id)
    if chapter_filter:
        verses = [(c, t) for c, t in verses if chapter_filter(c)]
    chunks = chunk_by_wordcount(verses, chunk_words)
    return [{"book": book_id, "label": label or book_id, "chunk_id": i, "text": t}
            for i, t in enumerate(chunks)]


def _parse_tokens(chunk_text):
    out = []
    for tok in chunk_text.split():
        surface, _, lemma = tok.partition("|")
        out.append((surface, lemma))
    return out


def extract_features_greek(texts):
    """Function-lemma relative frequencies + sentence/word stats."""
    rows = []
    for t in texts:
        pairs = _parse_tokens(t)
        n = len(pairs)
        surface_joined = " ".join(s for s, _ in pairs)
        counts = pd.Series([l for _, l in pairs]).value_counts()
        feat = {f"fw_{w}": counts.get(w, 0) / n * 1000 for w in GREEK_FUNCTION_LEMMAS}
        # Greek NT sentence breaks: period, ano teleia (semicolon), Greek question mark
        sents = re.split(r"[.;·]+", surface_joined)
        sents = [s for s in sents if s.strip()]
        slens = [len(GREEK_LETTER_RE.findall(s)) for s in sents]
        feat["avg_sent_len"] = np.mean(slens) if slens else 0
        feat["std_sent_len"] = np.std(slens) if slens else 0
        words_clean = [w.lower() for w in GREEK_LETTER_RE.findall(surface_joined)]
        feat["avg_word_len"] = np.mean([len(w) for w in words_clean]) if words_clean else 0
        feat["ttr"] = len(set(words_clean)) / n if n else 0
        feat["n_words"] = n
        rows.append(feat)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    corpus = []
    for b in BOOKS_GREEK:
        corpus += chunk_book(b)
    df = pd.DataFrame(corpus)
    df["group"] = df["book"].map(lambda b: BOOKS_GREEK[b][1])
    feats = extract_features_greek(df["text"].tolist())
    out = pd.concat([df.drop(columns="text"), feats], axis=1)
    out_dir = os.path.join(REPO_ROOT, "results")
    os.makedirs(out_dir, exist_ok=True)
    out.to_csv(os.path.join(out_dir, "greek_nt_features.csv"), index=False)
    print(out.groupby("book").size())
    print("features:", feats.shape)
    print(out.groupby("book")["n_words"].sum())
