"""
Verse-by-verse parallel reader: original Hebrew/Greek (word + transliteration
+ gloss) alongside the full KJV verse and, optionally, the full ESV verse.

This is a close-reading companion to the corpus-wide stylometry pipeline
(features_hebrew.py / features_greek.py) — it looks at one passage at a
time rather than running statistics across a whole book.

ESV sourcing: fetched on demand from the free Crossway ESV API
(https://api.esv.org), one verse at a time, cached in data/esv_cache.json.
Requires the user's own free API key in the ESV_API_KEY environment
variable (sign up at https://api.esv.org) — without it, the ESV column is
simply omitted. ESV text is never bulk-downloaded: Crossway's non-commercial
terms cap free API use at 500 verses and forbid reproducing a whole book, so
this module only ever fetches the specific verses the caller asks for.
"""
import json, os, re, unicodedata
import xml.etree.ElementTree as ET

import features_hebrew as fh
import features_greek as fg
from features import REPO_ROOT

HEBREW_LEXICON_DIR = os.environ.get("HEBREW_LEXICON_DIR", os.path.join(REPO_ROOT, "data", "HebrewLexicon"))
GLOSSES_PATH = os.path.join(fg.NESTLE_DIR, "glosses", "berean-interlinear-glosses.xml")
ESV_CACHE_PATH = os.path.join(REPO_ROOT, "data", "esv_cache.json")

PROCLITIC_GLOSS = {
    "c": "and", "b": "in/with", "k": "like/as", "l": "to/for",
    "m": "from", "d": "the", "i": "[interrog.]",
}

# Books this reader ships glosses/transliteration for (matches the plan's scope).
BOOK_INFO = {
    "Isaiah":     {"kjv": "Isaiah",     "hebrew": True,  "greek": None},
    "Romans":     {"kjv": "Romans",     "hebrew": False, "greek": "Rom"},
    "Hebrews":    {"kjv": "Hebrews",    "hebrew": False, "greek": "Heb"},
    "John":       {"kjv": "John",       "hebrew": False, "greek": "John"},
    "Revelation": {"kjv": "Revelation", "hebrew": False, "greek": "Rev"},
    "1Peter":     {"kjv": "1Peter",     "hebrew": False, "greek": "1Pet"},
    "2Peter":     {"kjv": "2Peter",     "hebrew": False, "greek": "2Pet"},
}

# --- Hebrew lexicon (Strong's number -> gloss/transliteration) ---
_HEB_LEXICON = None


def _load_hebrew_lexicon():
    global _HEB_LEXICON
    if _HEB_LEXICON is not None:
        return _HEB_LEXICON
    path = os.path.join(HEBREW_LEXICON_DIR, "HebrewStrong.xml")
    root = ET.parse(path).getroot()
    ns = {"o": "http://openscriptures.github.com/morphhb/namespace"}
    lex = {}
    for entry in root.findall("o:entry", ns):
        sid = entry.get("id", "").lstrip("H")
        w = entry.find("o:w", ns)
        meaning = entry.find("o:meaning", ns)
        first_def = meaning.find("o:def", ns) if meaning is not None else None
        if first_def is not None and first_def.text:
            gloss = first_def.text.strip()
        elif meaning is not None:
            gloss = "".join(meaning.itertext()).strip().split(",")[0]
        else:
            gloss = ""
        lex[sid] = {"xlit": w.get("xlit", "") if w is not None else "", "gloss": gloss}
    _HEB_LEXICON = lex
    return lex


def _hebrew_word_gloss(lemma_field):
    """Render a gloss + transliteration string for one OSHB lemma field."""
    lex = _load_hebrew_lexicon()
    parts = []
    for code in fh._lemma_morphemes(lemma_field):
        if code in PROCLITIC_GLOSS:
            parts.append(PROCLITIC_GLOSS[code])
        else:
            sid = re.sub(r"\D", "", code)
            entry = lex.get(sid)
            if entry:
                parts.append(f"{entry['gloss']} ({entry['xlit']})")
            else:
                parts.append(f"H{sid}")
    return "; ".join(parts)


# --- Greek glosses (Berean interlinear, matched by verse word order) ---
_GREEK_GLOSSES = None

GREEK_TO_LATIN = str.maketrans({
    "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "ē",
    "θ": "th", "ι": "i", "κ": "k", "λ": "l", "μ": "m", "ν": "n", "ξ": "x",
    "ο": "o", "π": "p", "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "υ": "y",
    "φ": "ph", "χ": "ch", "ψ": "ps", "ω": "ō",
})


def _greek_transliterate(word):
    letters_only = fg.GREEK_LETTER_RE.findall(word)
    stripped = "".join(c for c in unicodedata.normalize("NFD", "".join(letters_only))
                        if not unicodedata.combining(c))
    return stripped.lower().translate(GREEK_TO_LATIN)


HEBREW_TO_LATIN = str.maketrans({
    "א": "'", "ב": "b", "ג": "g", "ד": "d", "ה": "h", "ו": "v", "ז": "z",
    "ח": "ch", "ט": "t", "י": "y", "כ": "k", "ך": "k", "ל": "l", "מ": "m",
    "ם": "m", "נ": "n", "ן": "n", "ס": "s", "ע": "'", "פ": "p", "ף": "p",
    "צ": "tz", "ץ": "tz", "ק": "q", "ר": "r", "ש": "sh", "ת": "t",
})


def _hebrew_transliterate(word):
    return fh._strip_points(word).translate(HEBREW_TO_LATIN)


def _load_greek_glosses():
    global _GREEK_GLOSSES
    if _GREEK_GLOSSES is not None:
        return _GREEK_GLOSSES
    root = ET.parse(GLOSSES_PATH).getroot()
    out = {}
    for verse in root.findall(".//verse"):
        for w in verse.findall("w"):
            osis_id = w.get("osisId", "")
            book_cv, _, _wnum = osis_id.rpartition("!")
            if book_cv.count(".") < 2:
                continue  # a handful of upstream rows are missing osisId
            book, ch, vs = book_cv.rsplit(".", 2)
            gloss = (w.findtext("gloss") or "").strip()
            out.setdefault((book, int(ch), int(vs)), []).append(gloss)
    _GREEK_GLOSSES = out
    return out


# --- Original-language word retrieval ---
def get_original_words(book, chapter, verse):
    """Return [{"surface", "translit", "gloss"}, ...] for one verse."""
    info = BOOK_INFO[book]
    if info["hebrew"]:
        words = fh.load_isaiah_indexed().get((chapter, verse), [])
        return [{"surface": fh._strip_points(s), "translit": _hebrew_transliterate(s),
                 "gloss": _hebrew_word_gloss(l)} for s, l in words]
    if info["greek"]:
        words = fg.get_verse_words(info["greek"], chapter, verse)
        glosses = _load_greek_glosses().get((info["greek"], chapter, verse), [])
        out = []
        for i, (surface, lemma) in enumerate(words):
            out.append({
                "surface": surface,
                "translit": _greek_transliterate(surface),
                "gloss": glosses[i] if i < len(glosses) else lemma,
            })
        return out
    return []


# --- KJV ---
def get_kjv_verse(book, chapter, verse):
    """load_book (features.py) discards verse numbers when chunking, so read
    the KJV JSON directly here to keep verse-level addressing."""
    info = BOOK_INFO[book]
    path = os.path.join(REPO_ROOT, "data", "Bible-kjv", f"{info['kjv']}.json")
    data = json.load(open(path, encoding="utf-8"))
    for ch in data["chapters"]:
        if int(ch["chapter"]) == chapter:
            for v in ch["verses"]:
                if int(v["verse"]) == verse:
                    return v["text"]
    return None


# --- ESV (on-demand, cached, optional) ---
def _load_esv_cache():
    if os.path.exists(ESV_CACHE_PATH):
        return json.load(open(ESV_CACHE_PATH, encoding="utf-8"))
    return {}


def _save_esv_cache(cache):
    os.makedirs(os.path.dirname(ESV_CACHE_PATH), exist_ok=True)
    json.dump(cache, open(ESV_CACHE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def get_esv_verse(book, chapter, verse):
    """Fetch one verse from the free ESV API, cached locally. Returns None if
    ESV_API_KEY is unset or the request fails."""
    api_key = os.environ.get("ESV_API_KEY")
    if not api_key:
        return None
    key = f"{book} {chapter}:{verse}"
    cache = _load_esv_cache()
    if key in cache:
        return cache[key]
    import requests
    resp = requests.get(
        "https://api.esv.org/v3/passage/text/",
        params={"q": key, "include-headings": False, "include-footnotes": False,
                "include-verse-numbers": False, "include-short-copyright": False,
                "include-passage-references": False},
        headers={"Authorization": f"Token {api_key}"}, timeout=10,
    )
    if resp.status_code != 200:
        return None
    passages = resp.json().get("passages", [])
    text = passages[0].strip() if passages else None
    cache[key] = text
    _save_esv_cache(cache)
    return text


# --- Parallel table ---
def render_parallel_table(book, chapter, verses):
    """Return a list of row-dicts, one per verse: original words (with
    transliteration+gloss), full KJV text, full ESV text (or None)."""
    info = BOOK_INFO[book]
    rows = []
    for v in verses:
        words = get_original_words(book, chapter, v)
        rows.append({
            "ref": f"{book} {chapter}:{v}",
            "original_words": words,
            "kjv": get_kjv_verse(book, chapter, v),
            "esv": get_esv_verse(info["kjv"], chapter, v),
        })
    return rows


def print_parallel_table(book, chapter, verses):
    for row in render_parallel_table(book, chapter, verses):
        print(f"\n=== {row['ref']} ===")
        orig_line = "  ".join(f"{w['surface']}[{w['translit']}={w['gloss']}]" for w in row["original_words"])
        print("Original:", orig_line)
        print("KJV:     ", row["kjv"])
        print("ESV:     ", row["esv"] or "(set ESV_API_KEY to fetch)")


if __name__ == "__main__":
    print_parallel_table("Isaiah", 53, [5])
    print_parallel_table("Romans", 1, [1])
