"""
KJV Stylometry Pipeline
Loads KJV text, segments into chunks, extracts stylometric features
(function-word frequencies, sentence stats), and provides Burrows' Delta,
PCA, and classification utilities.
"""
import json, re, os
import numpy as np
import pandas as pd
from chunking import chunk_by_wordcount

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KJV_DIR = os.environ.get("KJV_DIR", os.path.join(REPO_ROOT, "data", "Bible-kjv"))

# ---------------------------------------------------------------
# 1. Metadata: traditional author, critical view, KJV translation company
# ---------------------------------------------------------------
# KJV companies (historical record):
#   First Westminster:  Genesis - 2 Kings
#   First Cambridge:    1 Chronicles - Song of Solomon
#   First Oxford:       Isaiah - Malachi
#   Second Oxford:      Gospels, Acts, Revelation
#   Second Westminster: Romans - Jude (all NT epistles)

BOOKS = {
    # name: (json file, traditional author, critical grouping, kjv company)
    "Isaiah":        ("Isaiah.json",        "Isaiah",  "split_1_39_40_66", "First Oxford"),
    "Romans":        ("Romans.json",        "Paul",    "undisputed",  "Second Westminster"),
    "1Corinthians":  ("1Corinthians.json",  "Paul",    "undisputed",  "Second Westminster"),
    "2Corinthians":  ("2Corinthians.json",  "Paul",    "undisputed",  "Second Westminster"),
    "Galatians":     ("Galatians.json",     "Paul",    "undisputed",  "Second Westminster"),
    "Philippians":   ("Philippians.json",   "Paul",    "undisputed",  "Second Westminster"),
    "1Thessalonians":("1Thessalonians.json","Paul",    "undisputed",  "Second Westminster"),
    "Philemon":      ("Philemon.json",      "Paul",    "undisputed",  "Second Westminster"),
    "Ephesians":     ("Ephesians.json",     "Paul",    "disputed_deutero", "Second Westminster"),
    "Colossians":    ("Colossians.json",    "Paul",    "disputed_deutero", "Second Westminster"),
    "2Thessalonians":("2Thessalonians.json","Paul",    "disputed_deutero", "Second Westminster"),
    "1Timothy":      ("1Timothy.json",      "Paul",    "pastoral",    "Second Westminster"),
    "2Timothy":      ("2Timothy.json",      "Paul",    "pastoral",    "Second Westminster"),
    "Titus":         ("Titus.json",         "Paul",    "pastoral",    "Second Westminster"),
    "Hebrews":       ("Hebrews.json",       "Paul(trad)", "non_pauline", "Second Westminster"),
    "1Peter":        ("1Peter.json",        "Peter",   "petrine_1",   "Second Westminster"),
    "2Peter":        ("2Peter.json",        "Peter",   "petrine_2",   "Second Westminster"),
    "John":          ("John.json",          "John",    "johannine_gospel", "Second Oxford"),
    "Revelation":    ("Revelation.json",    "John",    "johannine_apoc",   "Second Oxford"),
    "1John":         ("1John.json",         "John",    "johannine_epistle", "Second Westminster"),
    "2John":         ("2John.json",         "John",    "johannine_epistle", "Second Westminster"),
    "3John":         ("3John.json",         "John",    "johannine_epistle", "Second Westminster"),
    "Luke":          ("Luke.json",          "Luke",    "lukan_gospel",    "Second Oxford"),
    "Acts":          ("Acts.json",          "Luke",    "lukan_acts",      "Second Oxford"),
}

# 100 common English function words (style markers robust to topic)
FUNCTION_WORDS = """the and of to that in he shall for unto his i a not be
they it is with him them but as have was which all my thou me their ye you
this will from are were by we her she or when then out up upon so if at on
what there no man now also more before because into after об о can may might
do did done had has been am art hath thee thy your our us who whom whose
any every none both such same other another therefore wherefore yet
neither nor either while until against among through over under between""".split()
FUNCTION_WORDS = [w for w in FUNCTION_WORDS if w.isalpha() and w.isascii()]

WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")

def load_book(name):
    """Return list of (chapter:int, verse_text) tuples."""
    fn, *_ = BOOKS[name]
    data = json.load(open(os.path.join(KJV_DIR, fn)))
    out = []
    for ch in data["chapters"]:
        cnum = int(ch["chapter"])
        for v in ch["verses"]:
            out.append((cnum, v["text"]))
    return out

def chunk_book(name, chunk_words=1500, chapter_filter=None, label=None):
    """Split a book (optionally filtered to a chapter range) into ~chunk_words chunks."""
    verses = load_book(name)
    if chapter_filter:
        verses = [(c, t) for c, t in verses if chapter_filter(c)]
    chunks = chunk_by_wordcount(verses, chunk_words)
    return [{"book": name, "label": label or name, "chunk_id": i, "text": t}
            for i, t in enumerate(chunks)]

def extract_features(texts):
    """Function-word relative frequencies + sentence/word stats."""
    rows = []
    for t in texts:
        low = t.lower()
        words = WORD_RE.findall(low)
        n = len(words)
        counts = pd.Series(words).value_counts()
        feat = {f"fw_{w}": counts.get(w, 0) / n * 1000 for w in FUNCTION_WORDS}
        # sentence stats (KJV punctuation: . ? ! and ; as strong breaks)
        sents = re.split(r"[.?!;]+", t)
        sents = [s for s in sents if s.strip()]
        slens = [len(WORD_RE.findall(s.lower())) for s in sents]
        feat["avg_sent_len"] = np.mean(slens) if slens else 0
        feat["std_sent_len"] = np.std(slens) if slens else 0
        feat["avg_word_len"] = np.mean([len(w) for w in words])
        feat["ttr"] = len(set(words)) / n              # type-token ratio
        feat["n_words"] = n
        rows.append(feat)
    return pd.DataFrame(rows)

def burrows_delta(df_fw, train_idx):
    """Z-score function-word features on training rows; Delta = mean |z| distance."""
    mu = df_fw.loc[train_idx].mean()
    sd = df_fw.loc[train_idx].std().replace(0, 1e-9)
    return (df_fw - mu) / sd

if __name__ == "__main__":
    # Build the full chunked corpus
    corpus = []
    corpus += chunk_book("Isaiah", chapter_filter=lambda c: c <= 39, label="Isaiah_1-39")
    corpus += chunk_book("Isaiah", chapter_filter=lambda c: c >= 40, label="Isaiah_40-66")
    for b, meta in BOOKS.items():
        if b == "Isaiah": continue
        corpus += chunk_book(b)
    df = pd.DataFrame(corpus)
    meta_map = {b: m for b, m in BOOKS.items()}
    df["group"] = df["book"].map(lambda b: meta_map[b][2])
    df.loc[df.label == "Isaiah_1-39", "group"] = "proto_isaiah"
    df.loc[df.label == "Isaiah_40-66", "group"] = "deutero_trito_isaiah"
    df["company"] = df["book"].map(lambda b: meta_map[b][3])
    feats = extract_features(df["text"].tolist())
    out = pd.concat([df.drop(columns="text"), feats], axis=1)
    results_dir = os.path.join(REPO_ROOT, "results")
    os.makedirs(results_dir, exist_ok=True)
    out.to_csv(os.path.join(results_dir, "kjv_features.csv"), index=False)
    df[["book","label","chunk_id","group","company"]].to_csv(os.path.join(results_dir, "kjv_chunks_meta.csv"), index=False)
    print(out.groupby("label").size())
    print("features:", feats.shape)
