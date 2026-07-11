"""Shared word-count chunking logic used by the English/Hebrew/Greek loaders."""


def chunk_by_wordcount(verses, chunk_words=1500, word_count=lambda t: len(t.split())):
    """Group a list of (chapter, verse_text) tuples into ~chunk_words chunks.

    Chunks are contiguous verse runs whose total word count reaches
    chunk_words; a substantial remainder (>= half chunk_words) becomes its
    own chunk, a small remainder merges into the previous chunk, and a book
    smaller than one chunk becomes a single chunk.
    """
    chunks, cur, cur_n = [], [], 0
    for _, t in verses:
        cur.append(t)
        cur_n += word_count(t)
        if cur_n >= chunk_words:
            chunks.append(" ".join(cur)); cur, cur_n = [], 0
    if cur_n >= chunk_words * 0.5:          # keep substantial remainder
        chunks.append(" ".join(cur))
    elif cur and chunks:                     # merge small tail into last chunk
        chunks[-1] += " " + " ".join(cur)
    elif cur:                                # whole book smaller than one chunk
        chunks.append(" ".join(cur))
    return chunks
