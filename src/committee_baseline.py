"""Committee-effect baseline: how much stylistic difference does a KJV
translation company itself introduce, independent of authorship?

Design: compare a pair of books traditionally credited to the *same* author
but translated by *different* KJV companies, against a pair by the same
author translated by the *same* company. If the cross-committee pair
separates more than the same-committee pair, that's evidence the companies
introduce stylistic noise of their own on top of (or instead of) authorial
signal -- which would qualify how the rest of this project's "cannot be a
translation artifact" argument is read.

Pair 1 (cross-committee): Gospel of John (Second Oxford) vs 1-3 John
(Second Westminster). Unlike Revelation -- whose Johannine authorship is
contested in NT scholarship, and which is already tested elsewhere in this
project as an authorship split -- 1 John is the text stylistically closest
to John's Gospel among the Johannine corpus, making it a more credible
same-author test for isolating translator effect specifically.

Pair 2 (same-committee control): Luke vs Acts (both Second Oxford, both
traditionally attributed to Luke). No committee crossing here, so this is
the baseline for "normal" within-author variation the pipeline picks up
when translation company is held constant.
"""
import os
import pandas as pd

from features import REPO_ROOT, BOOKS, chunk_book, extract_features
from analysis import pca_plot, permutation_test, svm_cv_accuracy, svm_feature_weights


def build_corpus(books):
    corpus = []
    for b in books:
        corpus += chunk_book(b)
    df = pd.DataFrame(corpus)
    df["group"] = df["book"].map(lambda b: BOOKS[b][2])
    df["company"] = df["book"].map(lambda b: BOOKS[b][3])
    return df


if __name__ == "__main__":
    results_dir = os.path.join(REPO_ROOT, "results")
    fig_dir = os.path.join(results_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)

    results = []

    # ---- Pair 1: cross-committee, same traditional author (John) ----
    joh = build_corpus(["John", "1John", "2John", "3John"])
    feats = extract_features(joh["text"].tolist())
    fw_cols = [c for c in feats.columns if c.startswith("fw_")]
    style_cols = fw_cols + ["avg_sent_len", "std_sent_len", "avg_word_len", "ttr"]
    joh = pd.concat([joh.drop(columns="text"), feats], axis=1)

    pca_plot(joh, style_cols, "group",
              "Gospel of John vs 1-3 John: same traditional author,\n"
              "different KJV companies (2nd Oxford vs 2nd Westminster)",
              "fig5_johannine_committee.png", out_dir=fig_dir, annotate=True)
    obs, p = permutation_test(joh, style_cols, "group")
    min_n = joh.group.value_counts().min()
    acc = svm_cv_accuracy(joh, style_cols, "group") if min_n >= 5 else float("nan")
    results.append({"comparison": "John vs 1-3 John (cross-committee, same author)",
                     "centroid_dist": obs, "perm_p": p, "svm_cv_acc": acc, "n_chunks": len(joh)})
    svm_feature_weights(joh, style_cols, "group").to_csv(
        os.path.join(results_dir, "feature_weights_johannine_committee.csv"))

    # ---- Pair 2: same-committee control, same traditional author (Luke) ----
    luk = build_corpus(["Luke", "Acts"])
    feats2 = extract_features(luk["text"].tolist())
    luk = pd.concat([luk.drop(columns="text"), feats2], axis=1)

    pca_plot(luk, style_cols, "group",
              "Luke vs Acts: same traditional author, same KJV company\n(both 2nd Oxford)",
              "fig6_lukan_committee.png", out_dir=fig_dir)
    obs2, p2 = permutation_test(luk, style_cols, "group")
    min_n2 = luk.group.value_counts().min()
    acc2 = svm_cv_accuracy(luk, style_cols, "group") if min_n2 >= 5 else float("nan")
    results.append({"comparison": "Luke vs Acts (same-committee control, same author)",
                     "centroid_dist": obs2, "perm_p": p2, "svm_cv_acc": acc2, "n_chunks": len(luk)})

    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(results_dir, "committee_baseline_results.csv"), index=False)
    print(res_df.to_string(index=False))
