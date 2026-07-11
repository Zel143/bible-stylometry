"""Analysis: does original-language stylometric signal survive into KJV English?

pca_plot / permutation_test are parametrized by style_cols and an output
directory so they can be reused for the Hebrew/Greek original-language
notebook as well as the KJV English one (see notebooks/).
"""
import os
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pca_plot(sub, style_cols, color_key, title, fname, out_dir=None, annotate=False):
    out_dir = out_dir or os.path.join(REPO_ROOT, "results", "figures")
    os.makedirs(out_dir, exist_ok=True)
    X = StandardScaler().fit_transform(sub[style_cols])
    p = PCA(2).fit(X); XY = p.transform(X)
    fig, ax = plt.subplots(figsize=(8, 6))
    for g, m in zip(sorted(sub[color_key].unique()), "osv^DPX*<>"):
        mask = (sub[color_key] == g).values
        ax.scatter(XY[mask, 0], XY[mask, 1], label=g, marker=m, s=70, alpha=0.75)
    if annotate:
        for i, (x, y) in enumerate(XY):
            ax.annotate(sub.iloc[i]["book"][:6], (x, y), fontsize=6, alpha=0.6)
    ax.set_xlabel(f"PC1 ({p.explained_variance_ratio_[0]:.0%})")
    ax.set_ylabel(f"PC2 ({p.explained_variance_ratio_[1]:.0%})")
    ax.set_title(title); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(os.path.join(out_dir, fname), dpi=130); plt.close(fig)


def permutation_test(sub, style_cols, label_col, n_perm=5000, seed=0):
    """Test: is between-group centroid distance larger than chance?"""
    X = StandardScaler().fit_transform(sub[style_cols])
    y = (sub[label_col] == sorted(sub[label_col].unique())[0]).values
    def stat(yv):
        return np.linalg.norm(X[yv].mean(0) - X[~yv].mean(0))
    obs = stat(y)
    rng = np.random.default_rng(seed)
    null = [stat(rng.permutation(y)) for _ in range(n_perm)]
    p = (np.sum(np.array(null) >= obs) + 1) / (n_perm + 1)
    return obs, p


def svm_cv_accuracy(sub, style_cols, label_col, cv=5):
    X = StandardScaler().fit_transform(sub[style_cols])
    return cross_val_score(SVC(kernel="linear"), X, sub[label_col], cv=cv).mean()


def burrows_delta_z(df, fw_cols, reference_rows):
    """Z-score function-word columns against a reference subset's mean/std."""
    mu = df.loc[reference_rows, fw_cols].mean()
    sd = df.loc[reference_rows, fw_cols].std().replace(0, 1e-9)
    return (df[fw_cols] - mu) / sd


if __name__ == "__main__":
    results_dir = os.path.join(REPO_ROOT, "results")
    df = pd.read_csv(os.path.join(results_dir, "kjv_features.csv"))
    fw_cols = [c for c in df.columns if c.startswith("fw_")]
    style_cols = fw_cols + ["avg_sent_len", "std_sent_len", "avg_word_len", "ttr"]

    results = []

    # ---- CASE 1: Isaiah 1-39 vs 40-66 (same KJV company: First Oxford) ----
    isa = df[df.label.str.startswith("Isaiah")].reset_index(drop=True)
    pca_plot(isa, style_cols, "label", "Isaiah in KJV English: chs 1–39 vs 40–66\n(both translated by First Oxford Company)", "fig1_isaiah.png")
    obs, p = permutation_test(isa, style_cols, "label")
    acc = svm_cv_accuracy(isa, style_cols, "label")
    results.append(("Isaiah 1-39 vs 40-66", obs, p, acc, len(isa)))

    # ---- CASE 2: Pauline corpus (all Second Westminster Company) ----
    paul_groups = ["undisputed", "disputed_deutero", "pastoral", "non_pauline"]
    paul = df[df.group.isin(paul_groups)].reset_index(drop=True)
    pca_plot(paul, style_cols, "group", "Pauline corpus + Hebrews in KJV English\n(all translated by Second Westminster Company)", "fig2_paul.png", annotate=True)

    # Undisputed vs Pastorals
    up = df[df.group.isin(["undisputed", "pastoral"])].reset_index(drop=True)
    obs, p = permutation_test(up, style_cols, "group")
    results.append(("Undisputed Paul vs Pastorals", obs, p, np.nan, len(up)))
    # Undisputed vs Hebrews
    uh = df[df.group.isin(["undisputed", "non_pauline"])].reset_index(drop=True)
    obs, p = permutation_test(uh, style_cols, "group")
    acc = svm_cv_accuracy(uh, style_cols, "group")
    results.append(("Undisputed Paul vs Hebrews", obs, p, acc, len(uh)))

    # ---- CASE 3: Johannine (John: 2nd Oxford; Revelation: 2nd Oxford too) ----
    joh = df[df.group.isin(["johannine_gospel", "johannine_apoc"])].reset_index(drop=True)
    pca_plot(joh, style_cols, "group", "Gospel of John vs Revelation in KJV English\n(both translated by Second Oxford Company)", "fig3_john.png")
    obs, p = permutation_test(joh, style_cols, "group")
    acc = svm_cv_accuracy(joh, style_cols, "group")
    results.append(("John vs Revelation", obs, p, acc, len(joh)))

    # ---- CASE 4: 1 Peter vs 2 Peter (tiny sample — expect low power) ----
    pet = df[df.group.isin(["petrine_1", "petrine_2"])].reset_index(drop=True)
    obs, p = permutation_test(pet, style_cols, "group")
    results.append(("1 Peter vs 2 Peter", obs, p, np.nan, len(pet)))

    # ---- Burrows' Delta: attribute each disputed letter to nearest profile ----
    z = burrows_delta_z(df, fw_cols, df.index[df.group == "undisputed"])
    prof = {g: z[df.group == g].mean() for g in ["undisputed", "johannine_gospel", "johannine_apoc", "non_pauline"]}
    delta_rows = []
    for book in ["Ephesians","Colossians","2Thessalonians","1Timothy","2Timothy","Titus","Hebrews","1Peter","2Peter"]:
        zb = z[df.book == book].mean()
        ds = {g: np.mean(np.abs(zb - pv)) for g, pv in prof.items()}
        delta_rows.append({"book": book, **ds, "nearest": min(ds, key=ds.get)})
    delta_df = pd.DataFrame(delta_rows)

    res_df = pd.DataFrame(results, columns=["comparison","centroid_dist","perm_p","svm_cv_acc","n_chunks"])
    res_df.to_csv(os.path.join(results_dir, "results_tests.csv"), index=False)
    delta_df.to_csv(os.path.join(results_dir, "results_delta.csv"), index=False)
    print(res_df.to_string(index=False))
    print()
    print(delta_df.round(3).to_string(index=False))
