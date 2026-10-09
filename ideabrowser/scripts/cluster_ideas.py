"""Bottom-up clustering of the 424 featured ideas (no categories given).

Embeds title + pitch with a local sentence-transformers model (no text leaves the machine),
sweeps k-means over k, and reports the choice by silhouette and by stability across seeds.
Writes data/processed/clusters.csv (one row per featured idea: k-means label for each k,
plus 2-D coordinates for plotting) and prints a per-cluster summary for naming.

Newsletter-era pitches use section headings ("Why now", "The idea"), and those are stripped
so clusters group ideas rather than writing templates; the era mix per cluster is reported
as a check.

Options:
  --center-era   subtract each era's mean embedding first, so groups can't form around an
                 era's writing style (the newsletter era is 85% recognisable otherwise)
  --scope all    all 1,433 ideas from their titles alone (no pitch exists for most of them)

Usage: python projects/ideabrowser/scripts/cluster_ideas.py [--k K] [--center-era] [--scope all]
"""
import argparse
import re

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score, silhouette_score

from classify import DATA, load_ideas

MODEL = "sentence-transformers/all-mpnet-base-v2"
K_RANGE = range(6, 21)
SEEDS = range(5)
TEMPLATE = re.compile(r"\b(Why now|The idea|The problem|The product|How it works|How I'd start|Sources?:)\b", re.I)


def texts(ideas, titles_only=False):
    if titles_only:
        return list(ideas.title)
    return [f"{t}. {TEMPLATE.sub(' ', p)}" for t, p in zip(ideas.title, ideas.pitch)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, help="k to summarise (default: best by silhouette)")
    ap.add_argument("--center-era", action="store_true")
    ap.add_argument("--scope", choices=["featured", "all"], default="featured")
    args = ap.parse_args()
    titles_only = args.scope == "all"
    suffix = ("_all" if titles_only else "") + ("_centered" if args.center_era else "")

    ideas = load_ideas()
    if not titles_only:
        ideas = ideas[ideas.role == "featured"]
    ideas = ideas.reset_index(drop=True)
    emb = SentenceTransformer(MODEL).encode(texts(ideas, titles_only), normalize_embeddings=True,
                                            show_progress_bar=False)
    if args.center_era:
        for era in ideas.era.unique():
            emb[ideas.era == era] -= emb[ideas.era == era].mean(0)
        emb /= np.linalg.norm(emb, axis=1, keepdims=True)

    rows = []
    labels = {}
    for k in K_RANGE:
        runs = [KMeans(k, n_init=10, random_state=s).fit_predict(emb) for s in SEEDS]
        labels[k] = runs[0]
        stab = np.mean([adjusted_rand_score(runs[0], r) for r in runs[1:]])
        rows.append((k, silhouette_score(emb, runs[0], metric="cosine"), stab))
    sweep = pd.DataFrame(rows, columns=["k", "silhouette", "stability_ari"]).round(3)
    print(sweep.to_string(index=False))
    k = args.k or int(sweep.loc[sweep.silhouette.idxmax(), "k"])

    out = ideas[["key", "email_id", "era", "role", "date_utc", "title"]].copy()
    for kk, lab in labels.items():
        out[f"k{kk}"] = lab
    out[["x", "y"]] = PCA(2, random_state=0).fit_transform(emb)
    out.to_csv(DATA / f"clusters{suffix}.csv", index=False)
    np.save(DATA / f"embeddings{suffix}.npy", emb)

    # Summary for naming: size, era mix, distinctive words, the ideas nearest the centre.
    lab = labels[k]
    tf = TfidfVectorizer(stop_words="english", min_df=3, ngram_range=(1, 2))
    X = tf.fit_transform(texts(ideas, titles_only))
    vocab = np.array(tf.get_feature_names_out())
    print(f"\n=== k={k} ===")
    for c in range(k):
        idx = np.where(lab == c)[0]
        centre = emb[idx].mean(0)
        nearest = idx[np.argsort(-(emb[idx] @ centre))[:8]]
        lift = np.asarray(X[idx].mean(0)).ravel() - np.asarray(X.mean(0)).ravel()
        eras = ideas.era.iloc[idx].value_counts().reindex([1, 2, 3], fill_value=0).tolist()
        print(f"\n[{c}] n={len(idx)} eras(1/2/3)={eras}")
        print("   words: " + ", ".join(vocab[np.argsort(-lift)[:10]]))
        for i in nearest:
            print("   - " + ideas.title.iloc[i])


if __name__ == "__main__":
    main()
