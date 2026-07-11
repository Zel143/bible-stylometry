"""
Runs the same stylometric tests as src/analysis.py (permutation test, SVM
5-fold CV, Burrows' Delta) directly on the Hebrew and Greek originals,
instead of on the KJV English translation. Produces
results/original_language_results.csv and results/figures/orig_*.png,
mirroring the structure of results/results_tests.csv so the two can be
compared side by side (see notebooks/original_language_stylometry.ipynb).
"""
import os
import numpy as np
import pandas as pd

import features_hebrew as fh
import features_greek as fg
from analysis import pca_plot, permutation_test, svm_cv_accuracy, burrows_delta_z, REPO_ROOT

RESULTS_DIR = os.path.join(REPO_ROOT, "results")
FIG_DIR = os.path.join(RESULTS_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

results = []

# ---- Hebrew Isaiah 1-39 vs 40-66 ----
heb_corpus = []
heb_corpus += fh.chunk_isaiah(chapter_filter=lambda c: c <= 39, label="Isaiah_1-39")
heb_corpus += fh.chunk_isaiah(chapter_filter=lambda c: c >= 40, label="Isaiah_40-66")
heb_df = pd.DataFrame(heb_corpus)
heb_feats = fh.extract_features_hebrew(heb_df["text"].tolist())
heb_df = pd.concat([heb_df.drop(columns="text"), heb_feats], axis=1)
heb_style_cols = [c for c in heb_df.columns if c.startswith("fw_")] + ["avg_word_len", "std_word_len", "ttr"]

pca_plot(heb_df, heb_style_cols, "label",
         "Isaiah in the Hebrew original: chs 1–39 vs 40–66",
         "orig_fig1_isaiah_hebrew.png", out_dir=FIG_DIR)
obs, p = permutation_test(heb_df, heb_style_cols, "label")
acc = svm_cv_accuracy(heb_df, heb_style_cols, "label")
results.append(("Isaiah 1-39 vs 40-66 (Hebrew)", obs, p, acc, len(heb_df)))

# ---- Greek NT: Paul/Pastorals, Paul/Hebrews, John/Revelation, 1-2 Peter ----
grk_corpus = []
for b in fg.BOOKS_GREEK:
    grk_corpus += fg.chunk_book(b)
grk_df = pd.DataFrame(grk_corpus)
grk_df["group"] = grk_df["book"].map(lambda b: fg.BOOKS_GREEK[b][1])
grk_feats = fg.extract_features_greek(grk_df["text"].tolist())
grk_df = pd.concat([grk_df.drop(columns="text"), grk_feats], axis=1)
grk_fw_cols = [c for c in grk_df.columns if c.startswith("fw_")]
grk_style_cols = grk_fw_cols + ["avg_sent_len", "std_sent_len", "avg_word_len", "ttr"]

paul_groups = ["undisputed", "disputed_deutero", "pastoral", "non_pauline"]
paul = grk_df[grk_df.group.isin(paul_groups)].reset_index(drop=True)
pca_plot(paul, grk_style_cols, "group",
         "Pauline corpus + Hebrews in the Greek original",
         "orig_fig2_paul_greek.png", out_dir=FIG_DIR, annotate=True)

up = grk_df[grk_df.group.isin(["undisputed", "pastoral"])].reset_index(drop=True)
obs, p = permutation_test(up, grk_style_cols, "group")
results.append(("Undisputed Paul vs Pastorals (Greek)", obs, p, np.nan, len(up)))

uh = grk_df[grk_df.group.isin(["undisputed", "non_pauline"])].reset_index(drop=True)
obs, p = permutation_test(uh, grk_style_cols, "group")
acc = svm_cv_accuracy(uh, grk_style_cols, "group")
results.append(("Undisputed Paul vs Hebrews (Greek)", obs, p, acc, len(uh)))

joh = grk_df[grk_df.group.isin(["johannine_gospel", "johannine_apoc"])].reset_index(drop=True)
pca_plot(joh, grk_style_cols, "group",
         "Gospel of John vs Revelation in the Greek original",
         "orig_fig3_john_greek.png", out_dir=FIG_DIR)
obs, p = permutation_test(joh, grk_style_cols, "group")
acc = svm_cv_accuracy(joh, grk_style_cols, "group")
results.append(("John vs Revelation (Greek)", obs, p, acc, len(joh)))

pet = grk_df[grk_df.group.isin(["petrine_1", "petrine_2"])].reset_index(drop=True)
obs, p = permutation_test(pet, grk_style_cols, "group")
results.append(("1 Peter vs 2 Peter (Greek)", obs, p, np.nan, len(pet)))

# ---- Burrows' Delta on the Greek disputed letters ----
z = burrows_delta_z(grk_df, grk_fw_cols, grk_df.index[grk_df.group == "undisputed"])
prof = {g: z[grk_df.group == g].mean() for g in ["undisputed", "johannine_gospel", "johannine_apoc", "non_pauline"]}
delta_rows = []
for book in ["Eph", "Col", "2Thess", "1Tim", "2Tim", "Titus", "Heb", "1Pet", "2Pet"]:
    zb = z[grk_df.book == book].mean()
    ds = {g: np.mean(np.abs(zb - pv)) for g, pv in prof.items()}
    delta_rows.append({"book": book, **ds, "nearest": min(ds, key=ds.get)})
delta_df = pd.DataFrame(delta_rows)

res_df = pd.DataFrame(results, columns=["comparison", "centroid_dist", "perm_p", "svm_cv_acc", "n_chunks"])
res_df.to_csv(os.path.join(RESULTS_DIR, "original_language_results.csv"), index=False)
delta_df.to_csv(os.path.join(RESULTS_DIR, "original_language_delta.csv"), index=False)

if __name__ == "__main__":
    print(res_df.to_string(index=False))
    print()
    print(delta_df.round(3).to_string(index=False))
