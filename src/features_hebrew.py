"""
Hebrew Stylometry Pipeline
Loads the Hebrew Isaiah text (Westminster Leningrad Codex, via the Open
Scriptures Hebrew Bible morphology project), chunks it, and extracts
stylometric features analogous to features.py's English pipeline.

Unlike English, Hebrew attaches conjunctions/prepositions/the article as
prefixes onto the following word rather than as separate words (e.g.
"and Jerusalem" is one graphic word, וִ/ירוּשָׁלִָם). OSHB already marks the
morpheme boundary with "/" in both the surface text and the lemma field, so
function-word frequency here is computed over *morphemes* (prefixes counted
separately from their host word) rather than over whitespace-delimited
words, using the lemma/Strong's-number field rather than surface spelling.
"""
import os, re, unicodedata
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from chunking import chunk_by_wordcount

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MORPHHB_DIR = os.environ.get("MORPHHB_DIR", os.path.join(REPO_ROOT, "data", "morphhb"))
OSIS_NS = {"o": "http://www.bibletechnologies.net/2003/OSIS/namespace"}

# Proclitic morphemes attached to the following word in OSHB's lemma coding
# (conjunction, prepositions, article, interrogative-he).
PROCLITIC_CODES = {"c": "conj_vav", "b": "prep_be", "k": "prep_ke",
                    "l": "prep_le", "m": "prep_min", "d": "article_ha", "i": "interrog_he"}

# High-frequency, topic-robust Hebrew function words, by (unsuffixed) Strong's number.
CONTENT_FUNCTION_LEMMAS = {
    "853": "et_dom", "834": "asher_rel", "3588": "ki_causal", "3808": "lo_neg",
    "3605": "kol_all", "5921": "al_upon", "413": "el_to", "5973": "im_with",
    "1931": "hu_pron3ms", "2088": "zeh_this", "6310": "peh_mouth_idiom",
    "3117": "yom_day",
}
HEBREW_FUNCTION_KEYS = list(PROCLITIC_CODES.values()) + list(CONTENT_FUNCTION_LEMMAS.values())

HEBREW_POINTS_RE = re.compile(r"[֑-ֽֿ-ׇ]")  # niqqud + cantillation


def _strip_points(word):
    return HEBREW_POINTS_RE.sub("", unicodedata.normalize("NFC", word))


def _lemma_morphemes(lemma_field):
    """First space-separated token of the lemma field, split on '/' proclitic boundaries."""
    if not lemma_field:
        return []
    return lemma_field.split()[0].split("/")


def _parse_book_xml(fname):
    """Return list of (chapter:int, verse:int, [(surface, lemma), ...]) for any OSHB/WLC book file."""
    path = os.path.join(MORPHHB_DIR, "wlc", fname)
    root = ET.parse(path).getroot()
    out = []
    for chapter in root.findall(".//o:chapter", OSIS_NS):
        cnum = int(chapter.get("osisID").split(".")[1])
        for verse in chapter.findall("o:verse", OSIS_NS):
            vnum = int(verse.get("osisID").split(".")[2])
            words = []
            for w in verse.findall("o:w", OSIS_NS):
                surface = (w.text or "").strip()
                if not surface:
                    continue
                words.append((surface, w.get("lemma", "")))
            if words:
                out.append((cnum, vnum, words))
    return out


def _parse_isaiah_xml():
    """Return list of (chapter:int, verse:int, [(surface, lemma), ...])."""
    return _parse_book_xml("Isa.xml")


# OSIS book id -> WLC filename, for the Pentateuch (documentary-hypothesis extension).
PENTATEUCH_FILES = {"Gen": "Gen.xml", "Exod": "Exod.xml", "Lev": "Lev.xml", "Num": "Num.xml"}


def load_book(book_id):
    """Return list of (chapter:int, verse_text:str) tuples for any Pentateuch book id."""
    return [(c, " ".join(f"{s}|{l}" for s, l in words))
            for c, _v, words in _parse_book_xml(PENTATEUCH_FILES[book_id])]


def chunk_book(book_id, chapter_filter=None, chunk_words=1500, label=None):
    verses = load_book(book_id)
    if chapter_filter:
        verses = [(c, t) for c, t in verses if chapter_filter(c)]
    chunks = chunk_by_wordcount(verses, chunk_words)
    return [{"book": book_id, "label": label or book_id, "chunk_id": i, "text": t}
            for i, t in enumerate(chunks)]


def load_isaiah():
    """Return list of (chapter:int, verse_text:str) tuples.

    verse_text is a space-joined string of "surface|lemma" tokens, one per
    OSHB <w> element, so downstream chunking can still split on whitespace
    to count words while retaining the morphological lemma needed for
    function-morpheme frequencies.
    """
    return [(c, " ".join(f"{s}|{l}" for s, l in words))
            for c, _v, words in _parse_isaiah_xml()]


def load_isaiah_indexed():
    """Return {(chapter, verse): [(surface, lemma), ...]} for verse-level lookup."""
    return {(c, v): words for c, v, words in _parse_isaiah_xml()}


def chunk_isaiah(chapter_filter=None, chunk_words=1500, label=None):
    verses = load_isaiah()
    if chapter_filter:
        verses = [(c, t) for c, t in verses if chapter_filter(c)]
    chunks = chunk_by_wordcount(verses, chunk_words)
    return [{"book": "Isaiah", "label": label or "Isaiah", "chunk_id": i, "text": t}
            for i, t in enumerate(chunks)]


def _parse_tokens(chunk_text):
    """Split a chunk's "surface|lemma" tokens into (surface, lemma) pairs."""
    out = []
    for tok in chunk_text.split():
        surface, _, lemma = tok.partition("|")
        out.append((surface, lemma))
    return out


def extract_features_hebrew(texts):
    """Morpheme-frequency (proclitics + content function words) + word/verse stats."""
    rows = []
    for t in texts:
        pairs = _parse_tokens(t)
        n = len(pairs)
        morph_counts = {k: 0 for k in HEBREW_FUNCTION_KEYS}
        word_lens = []
        surfaces = []
        for surface, lemma in pairs:
            consonantal = _strip_points(surface)
            for seg in consonantal.split("/"):
                word_lens.append(len(seg))
            surfaces.append(consonantal)
            for code in _lemma_morphemes(lemma):
                if code in PROCLITIC_CODES:
                    morph_counts[PROCLITIC_CODES[code]] += 1
                elif code in CONTENT_FUNCTION_LEMMAS:
                    morph_counts[CONTENT_FUNCTION_LEMMAS[code]] += 1
        feat = {f"fw_{k}": morph_counts[k] / n * 1000 for k in HEBREW_FUNCTION_KEYS}
        feat["avg_word_len"] = np.mean(word_lens) if word_lens else 0
        feat["std_word_len"] = np.std(word_lens) if word_lens else 0
        feat["ttr"] = len(set(surfaces)) / n if n else 0
        feat["n_words"] = n
        rows.append(feat)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    corpus = []
    corpus += chunk_isaiah(chapter_filter=lambda c: c <= 39, label="Isaiah_1-39")
    corpus += chunk_isaiah(chapter_filter=lambda c: c >= 40, label="Isaiah_40-66")
    df = pd.DataFrame(corpus)
    feats = extract_features_hebrew(df["text"].tolist())
    out = pd.concat([df.drop(columns="text"), feats], axis=1)
    out_dir = os.path.join(REPO_ROOT, "results")
    os.makedirs(out_dir, exist_ok=True)
    out.to_csv(os.path.join(out_dir, "hebrew_isaiah_features.csv"), index=False)
    print(out.groupby("label").size())
    print("features:", feats.shape)
    print(out.groupby("label")["n_words"].sum())
