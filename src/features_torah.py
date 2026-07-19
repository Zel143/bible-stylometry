"""
Documentary-hypothesis extension: does the classic Priestly (P) vs.
non-Priestly (J/E) source split proposed for the Pentateuch show up as a
stylometric signal, the way Koppel et al. (2011) and Yoffe et al. (2023,
2025) found using more elaborate unsupervised methods?

This project's Hebrew extension so far only covers Isaiah. Genesis, Exodus,
Leviticus, and Numbers are also available in the OSHB/WLC data
(`data/morphhb/wlc/`), so the same permutation-test/SVM pipeline can be
pointed at them directly.

Source-critical scope: this uses *whole-chapter* granularity (this project's
existing chunking only filters by chapter number, not verse), so only
chapters that are overwhelmingly and uncontroversially attributed to one
source in mainstream documentary-hypothesis scholarship are included.
Chapters where P and J/E material are known to be verse-by-verse interwoven
(e.g. the flood narrative, Genesis 6-9; the Babel/genealogy material,
Genesis 10-11; the plagues/Passover material, Exodus 6-7 and 12; the Korah
cycle, Numbers 16-17, 20) are deliberately excluded from both groups rather
than guessed at, since a wrong whole-chapter call there would manufacture
signal rather than measure it. Chapter assignments follow the widely-cited
summary of the Priestly source's contents (e.g. the "Priestly source"
literature summarized in docs/background.md's tradition), not a
verse-by-verse critical edition -- so treat this as a first-pass replication
at a coarser resolution than Friedman (2003) or Yoffe et al.'s own source
division, not a verse-exact reproduction of it.
"""
import os
import numpy as np
import pandas as pd

import features_hebrew as fh
from analysis import pca_plot, permutation_test, svm_cv_accuracy, svm_feature_weights, REPO_ROOT

RESULTS_DIR = os.path.join(REPO_ROOT, "results")
FIG_DIR = os.path.join(RESULTS_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Chapters overwhelmingly attributed to P (Priestly): legal/cultic/genealogical
# material, not narrative. Excludes chapters known to interweave P with J/E.
P_CHAPTERS = {
    "Gen": {1, 17},
    "Exod": {25, 26, 27, 28, 29, 30, 31, 35, 36, 37, 38, 39, 40},
    "Lev": set(range(1, 28)),  # the whole book: cultic law, no J/E narrative competes for it
    "Num": {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 18, 19, 26, 27, 28, 29, 30, 33, 34, 35, 36},
}

# Chapters overwhelmingly attributed to J/E: narrative, non-priestly.
NONP_CHAPTERS = {
    "Gen": {3, 4, 12, 13, 15, 16, 18, 19, 20, 21, 22, 24, 27, 28, 29, 30, 31, 32, 33, 34,
            37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48, 50},
    "Exod": {1, 2, 3, 4, 5, 8, 9, 10, 11, 13, 14, 15},
    "Num": {11, 12, 13, 14, 21, 22, 23, 24},
}


def build_group(chapter_map, group_label):
    corpus = []
    for book_id, chapters in chapter_map.items():
        corpus += fh.chunk_book(book_id, chapter_filter=lambda c, chs=chapters: c in chs,
                                 label=f"{book_id}_{group_label}")
    df = pd.DataFrame(corpus)
    df["group"] = group_label
    return df


if __name__ == "__main__":
    p_df = build_group(P_CHAPTERS, "P")
    nonp_df = build_group(NONP_CHAPTERS, "non_P")
    df = pd.concat([p_df, nonp_df], ignore_index=True)

    feats = fh.extract_features_hebrew(df["text"].tolist())
    df = pd.concat([df.drop(columns="text"), feats], axis=1)
    fw_cols = [c for c in df.columns if c.startswith("fw_")]
    style_cols = fw_cols + ["avg_word_len", "std_word_len", "ttr"]

    df.to_csv(os.path.join(RESULTS_DIR, "torah_p_nonp_features.csv"), index=False)

    pca_plot(df, style_cols, "group",
             "Pentateuch (Gen/Exod/Lev/Num) in the Hebrew original:\nPriestly (P) vs. non-Priestly (J/E) chapters",
             "fig7_torah_p_nonp.png", out_dir=FIG_DIR, annotate=True)
    obs, p = permutation_test(df, style_cols, "group")
    acc = svm_cv_accuracy(df, style_cols, "group")
    svm_feature_weights(df, style_cols, "group").to_csv(
        os.path.join(RESULTS_DIR, "feature_weights_torah_p_nonp.csv"))

    res_df = pd.DataFrame([{"comparison": "Priestly (P) vs non-Priestly (J/E) Pentateuch chapters",
                             "centroid_dist": obs, "perm_p": p, "svm_cv_acc": acc, "n_chunks": len(df)}])
    res_df.to_csv(os.path.join(RESULTS_DIR, "torah_p_nonp_results.csv"), index=False)
    print(res_df.to_string(index=False))
    print()
    print(df.groupby(["book", "group"]).size())
    print()
    print("total words:", df.groupby("group")["n_words"].sum().to_dict())
