"""
World English Bible (WEB) Stylometry Pipeline
Loads the WEB text (public domain, modern-English translation, produced by
an entirely different translation process/era than the KJV) and extracts
features analogous to features.py's KJV pipeline, so the same tests can be
rerun on a second, independent translation. If a split reproduces in both
the KJV and the WEB, that's stronger evidence it's authorial rather than a
KJV-specific translation artifact.

The WEB JSON format is a flat list of typed entries (paragraph/line/stanza
markers plus text runs); a single verse's text is sometimes split across
multiple consecutive "text" entries (e.g. poetic quotations broken across
line boundaries), so they're grouped by (chapter, verse) and concatenated
before chunking.
"""
import json, os
import pandas as pd
from chunking import chunk_by_wordcount
from features import BOOKS, extract_features  # noqa: F401  (extract_features reused as-is)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.environ.get("WEB_DIR", os.path.join(REPO_ROOT, "data", "WEB", "json"))

# internal book name (matches features.py:BOOKS keys) -> WEB json filename
WEB_FILES = {
    "Isaiah":         "isaiah.json",
    "Romans":         "romans.json",
    "1Corinthians":   "1corinthians.json",
    "2Corinthians":   "2corinthians.json",
    "Galatians":      "galatians.json",
    "Philippians":    "philippians.json",
    "1Thessalonians": "1thessalonians.json",
    "Philemon":       "philemon.json",
    "Ephesians":      "ephesians.json",
    "Colossians":     "colossians.json",
    "2Thessalonians": "2thessalonians.json",
    "1Timothy":       "1timothy.json",
    "2Timothy":       "2timothy.json",
    "Titus":          "titus.json",
    "Hebrews":        "hebrews.json",
    "1Peter":         "1peter.json",
    "2Peter":         "2peter.json",
    "John":           "john.json",
    "Revelation":     "revelation.json",
}


def load_book(name):
    """Return list of (chapter:int, verse_text) tuples, in verse order."""
    fn = WEB_FILES[name]
    entries = json.load(open(os.path.join(WEB_DIR, fn), encoding="utf-8"))
    verses = {}
    for e in entries:
        if "value" not in e:
            continue
        key = (e["chapterNumber"], e["verseNumber"])
        verses.setdefault(key, []).append(e["value"])
    return [(c, " ".join(parts)) for (c, v), parts in sorted(verses.items())]


def chunk_book(name, chunk_words=1500, chapter_filter=None, label=None):
    """Split a book (optionally filtered to a chapter range) into ~chunk_words chunks."""
    verses = load_book(name)
    if chapter_filter:
        verses = [(c, t) for c, t in verses if chapter_filter(c)]
    chunks = chunk_by_wordcount(verses, chunk_words)
    return [{"book": name, "label": label or name, "chunk_id": i, "text": t}
            for i, t in enumerate(chunks)]


if __name__ == "__main__":
    corpus = []
    corpus += chunk_book("Isaiah", chapter_filter=lambda c: c <= 39, label="Isaiah_1-39")
    corpus += chunk_book("Isaiah", chapter_filter=lambda c: c >= 40, label="Isaiah_40-66")
    for b in WEB_FILES:
        if b == "Isaiah":
            continue
        corpus += chunk_book(b)
    df = pd.DataFrame(corpus)
    df["group"] = df["book"].map(lambda b: BOOKS[b][2])
    df.loc[df.label == "Isaiah_1-39", "group"] = "proto_isaiah"
    df.loc[df.label == "Isaiah_40-66", "group"] = "deutero_trito_isaiah"
    feats = extract_features(df["text"].tolist())
    out = pd.concat([df.drop(columns="text"), feats], axis=1)
    results_dir = os.path.join(REPO_ROOT, "results")
    os.makedirs(results_dir, exist_ok=True)
    out.to_csv(os.path.join(results_dir, "web_features.csv"), index=False)
    print(out.groupby("label").size())
    print("features:", feats.shape)
