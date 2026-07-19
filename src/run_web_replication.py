"""
Runs the same stylometric tests as src/analysis.py (permutation test, SVM
5-fold CV) on the World English Bible (WEB) instead of the KJV, to check
whether the project's splits reproduce on a second, independent public-domain
translation. Produces results/web_replication_results.csv and
results/figures/web_fig*.png, mirroring the structure of
results/results_tests.csv so KJV and WEB results can be compared side by side.
"""
import os
import numpy as np
import pandas as pd

import features_web as fw
from analysis import pca_plot, permutation_test, svm_cv_accuracy, REPO_ROOT

RESULTS_DIR = os.path.join(REPO_ROOT, "results")
FIG_DIR = os.path.join(RESULTS_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

corpus = []
corpus += fw.chunk_book("Isaiah", chapter_filter=lambda c: c <= 39, label="Isaiah_1-39")
corpus += fw.chunk_book("Isaiah", chapter_filter=lambda c: c >= 40, label="Isaiah_40-66")
for b in fw.WEB_FILES:
    if b == "Isaiah":
        continue
    corpus += fw.chunk_book(b)
df = pd.DataFrame(corpus)
df["group"] = df["book"].map(lambda b: fw.BOOKS[b][2])
df.loc[df.label == "Isaiah_1-39", "group"] = "proto_isaiah"
df.loc[df.label == "Isaiah_40-66", "group"] = "deutero_trito_isaiah"
feats = fw.extract_features(df["text"].tolist())
df = pd.concat([df.drop(columns="text"), feats], axis=1)
fw_cols = [c for c in df.columns if c.startswith("fw_")]
style_cols = fw_cols + ["avg_sent_len", "std_sent_len", "avg_word_len", "ttr"]

results = []

# ---- Isaiah 1-39 vs 40-66 ----
isa = df[df.label.str.startswith("Isaiah")].reset_index(drop=True)
pca_plot(isa, style_cols, "label", "Isaiah in WEB English: chs 1-39 vs 40-66",
         "web_fig1_isaiah.png", out_dir=FIG_DIR)
obs, p = permutation_test(isa, style_cols, "label")
acc = svm_cv_accuracy(isa, style_cols, "label")
results.append(("Isaiah 1-39 vs 40-66 (WEB)", obs, p, acc, len(isa)))

# ---- Pauline corpus + Hebrews ----
paul_groups = ["undisputed", "disputed_deutero", "pastoral", "non_pauline"]
paul = df[df.group.isin(paul_groups)].reset_index(drop=True)
pca_plot(paul, style_cols, "group", "Pauline corpus + Hebrews in WEB English",
         "web_fig2_paul.png", out_dir=FIG_DIR, annotate=True)

up = df[df.group.isin(["undisputed", "pastoral"])].reset_index(drop=True)
obs, p = permutation_test(up, style_cols, "group")
results.append(("Undisputed Paul vs Pastorals (WEB)", obs, p, np.nan, len(up)))

uh = df[df.group.isin(["undisputed", "non_pauline"])].reset_index(drop=True)
obs, p = permutation_test(uh, style_cols, "group")
acc = svm_cv_accuracy(uh, style_cols, "group")
results.append(("Undisputed Paul vs Hebrews (WEB)", obs, p, acc, len(uh)))

# ---- Gospel of John vs Revelation ----
joh = df[df.group.isin(["johannine_gospel", "johannine_apoc"])].reset_index(drop=True)
pca_plot(joh, style_cols, "group", "Gospel of John vs Revelation in WEB English",
         "web_fig3_john.png", out_dir=FIG_DIR)
obs, p = permutation_test(joh, style_cols, "group")
acc = svm_cv_accuracy(joh, style_cols, "group")
results.append(("John vs Revelation (WEB)", obs, p, acc, len(joh)))

# ---- 1 Peter vs 2 Peter ----
pet = df[df.group.isin(["petrine_1", "petrine_2"])].reset_index(drop=True)
obs, p = permutation_test(pet, style_cols, "group")
results.append(("1 Peter vs 2 Peter (WEB)", obs, p, np.nan, len(pet)))

res_df = pd.DataFrame(results, columns=["comparison", "centroid_dist", "perm_p", "svm_cv_acc", "n_chunks"])
res_df.to_csv(os.path.join(RESULTS_DIR, "web_replication_results.csv"), index=False)

if __name__ == "__main__":
    print(res_df.to_string(index=False))
