"""Genre control: does the Pastorals split survive regressing out topic?

The Pastorals (1-2 Timothy, Titus) are famous for church-organization content
(bishops, deacons, elders, sound doctrine) that the undisputed letters barely
touch. Function words are chosen to be topic-robust, but subject matter can
still leak into sentence-length/type-token style stats, and heavy repetition
of a topic's core nouns can pull even function-word co-occurrence patterns.

This module fits an LDA topic model on content words (function words and
stopwords excluded) across the Pauline corpus + Hebrews, gets each chunk's
topic distribution, and residualizes every style feature (fw_* plus the
sentence/word stats) against topic proportions via OLS. If the undisputed-
vs-pastoral separation survives on the residualized features, topic isn't
what's driving it; if it collapses, the split is at least partly genre.

Hebrews is included as a same-corpus control: it's a robust, uncontested
split (see results_tests.csv), so if genre-controlling collapses it too,
that would suggest the control itself is destroying real authorial signal
rather than just genre confound.
"""
import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.linear_model import LinearRegression

from features import REPO_ROOT, BOOKS, chunk_book, extract_features, FUNCTION_WORDS
from analysis import pca_plot, permutation_test, svm_cv_accuracy

N_TOPICS = 6
FUNCTION_WORD_SET = set(FUNCTION_WORDS)


def build_pauline_corpus():
    """Second-Westminster-company corpus: undisputed/deutero/pastoral Paul + Hebrews."""
    groups = {"undisputed", "disputed_deutero", "pastoral", "non_pauline"}
    corpus = []
    for b, meta in BOOKS.items():
        if meta[2] in groups:
            corpus += chunk_book(b)
    df = pd.DataFrame(corpus)
    df["group"] = df["book"].map(lambda b: BOOKS[b][2])
    return df


def fit_topics(texts, n_topics=N_TOPICS, seed=0):
    """Fit LDA on content words only (function words / stopwords stripped out)."""
    vec = CountVectorizer(lowercase=True, token_pattern=r"[a-z]+",
                           stop_words=list(FUNCTION_WORD_SET), min_df=2)
    dtm = vec.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=seed,
                                     learning_method="batch", max_iter=50)
    doc_topic = lda.fit_transform(dtm)
    return doc_topic, lda, vec


def top_words_per_topic(lda, vec, n_words=12):
    terms = np.array(vec.get_feature_names_out())
    rows = []
    for k, comp in enumerate(lda.components_):
        top = terms[np.argsort(comp)[::-1][:n_words]]
        rows.append({"topic": k, "top_words": ", ".join(top)})
    return pd.DataFrame(rows)


def residualize(style_df, topic_df):
    """Regress each style column on topic proportions (OLS), return residuals.

    One topic column is dropped to avoid collinearity (proportions sum to 1).
    """
    X = topic_df.values[:, 1:]
    resid = {}
    for col in style_df.columns:
        y = style_df[col].values
        reg = LinearRegression().fit(X, y)
        resid[col] = y - reg.predict(X)
    return pd.DataFrame(resid, index=style_df.index)


def run_comparison(df, style_cols, group_a, group_b, label, cv=5):
    sub = df[df.group.isin([group_a, group_b])].reset_index(drop=True)
    obs, p = permutation_test(sub, style_cols, "group")
    min_class_n = sub.group.value_counts().min()
    # skip CV accuracy when a class is smaller than the fold count: sklearn
    # can't stratify properly and the resulting number is overoptimistic
    # (matches the convention in analysis.py's main script)
    acc = svm_cv_accuracy(sub, style_cols, "group", cv=cv) if min_class_n >= cv else np.nan
    return {"comparison": label, "centroid_dist": obs, "perm_p": p,
            "svm_cv_acc": acc, "n_chunks": len(sub)}


if __name__ == "__main__":
    results_dir = os.path.join(REPO_ROOT, "results")
    fig_dir = os.path.join(results_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)

    df = build_pauline_corpus()
    feats = extract_features(df["text"].tolist())
    fw_cols = [c for c in feats.columns if c.startswith("fw_")]
    style_cols = fw_cols + ["avg_sent_len", "std_sent_len", "avg_word_len", "ttr"]

    doc_topic, lda, vec = fit_topics(df["text"].tolist())
    topic_cols = [f"topic_{k}" for k in range(N_TOPICS)]
    topic_df = pd.DataFrame(doc_topic, columns=topic_cols)
    top_words_per_topic(lda, vec).to_csv(os.path.join(results_dir, "genre_control_topics.csv"), index=False)

    full = pd.concat([df.drop(columns="text"), feats, topic_df], axis=1)

    resid_style = residualize(full[style_cols], topic_df)
    resid_full = pd.concat([full[["book", "group"]], resid_style], axis=1)

    pca_plot(full, style_cols, "group", "Pauline corpus + Hebrews: raw style features",
             "fig4_genre_raw.png", out_dir=fig_dir)
    pca_plot(resid_full, style_cols, "group", "Pauline corpus + Hebrews: style features residualized on LDA topic",
             "fig4_genre_residualized.png", out_dir=fig_dir)

    results = []
    results.append(run_comparison(full, style_cols, "undisputed", "pastoral", "Undisputed vs Pastorals (raw)"))
    results.append(run_comparison(resid_full, style_cols, "undisputed", "pastoral", "Undisputed vs Pastorals (topic-residualized)"))
    results.append(run_comparison(full, style_cols, "undisputed", "non_pauline", "Undisputed vs Hebrews (raw)"))
    results.append(run_comparison(resid_full, style_cols, "undisputed", "non_pauline", "Undisputed vs Hebrews (topic-residualized)"))

    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(results_dir, "genre_control_results.csv"), index=False)
    print(res_df.to_string(index=False))
    print()
    print(top_words_per_topic(lda, vec).to_string(index=False))
