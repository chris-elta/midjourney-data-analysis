"""Our own analysis pipeline for succinctly/midjourney-prompts (Part 1b).

Usage (from the repo root, after fetch_data.py):
    PYTHONPATH=analysis/.deps python3 analysis/pipeline.py

Stages
  1. Load the three Parquet splits and check them against MANIFEST.json.
  2. Audit data quality: fragments, duplicates, overlap between splits.
  3. Build the clean prompts: real prompts only, repeats removed.
  4. RQ1  What does a prompt look like? (length, parameters, aspect ratios)
  5. RQ2  How often do prompts cite artists or use "quality booster" phrases?
  6. RQ3  What themes do prompts cover? (TF-IDF + NMF topics, with a
          stability check across random subsamples)
  7. RQ4  Hypothesis tests with effect sizes.

Outputs
  analysis/results/results.json      every number the paper reports
  analysis/results/environment.json  Python and library versions
  analysis/results/topics.csv        top words per topic
  part1-paper/tables/*.tex           LaTeX tables, \\input by the paper
  part1-paper/figures/*.pdf          figures, \\includegraphics by the paper
  analysis/data/midjourney_prompts_all.csv  one file to give the AI tool
"""
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

import prompt_utils

SEED = 9200
N_TOPICS = 10
N_STABILITY_RUNS = 5
SUBSAMPLE_FRAC = 0.8
TOP_WORDS = 10

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw"
RESULTS = HERE / "results"
PAPER = HERE.parent / "part1-paper"
TABLES = PAPER / "tables"
FIGURES = PAPER / "figures"
SPLITS = ("train", "validation", "test")

R = {}  # every reported number goes in here


def log(msg):
    print(msg, file=sys.stderr)


# --------------------------------------------------------------------------
# 1. Load
# --------------------------------------------------------------------------
def load() -> pd.DataFrame:
    manifest = json.loads((RAW / "MANIFEST.json").read_text())
    frames = []
    for split in SPLITS:
        path = RAW / f"{split}.parquet"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != manifest["files"][split]["sha256"]:
            raise SystemExit(f"{path} does not match MANIFEST.json; re-run fetch_data.py")
        frames.append(pd.read_parquet(path).assign(split=split))
    df = pd.concat(frames, ignore_index=True)
    df["text"] = df["text"].fillna("")
    R["raw"] = {
        "rows": int(len(df)),
        "rows_by_split": df["split"].value_counts().reindex(SPLITS).astype(int).to_dict(),
        "sha256": {s: manifest["files"][s]["sha256"] for s in SPLITS},
    }
    return df


# --------------------------------------------------------------------------
# 2. Audit
# --------------------------------------------------------------------------
def audit(df: pd.DataFrame) -> pd.DataFrame:
    df["norm"] = df["text"].map(prompt_utils.normalise)
    df["fragment"] = df["text"].map(prompt_utils.fragment_type)

    chars = df["text"].str.len()
    R["audit"] = {
        "chars_median": float(chars.median()),
        "chars_q1": float(chars.quantile(0.25)),
        "chars_q3": float(chars.quantile(0.75)),
        "chars_max": int(chars.max()),
        "exact_duplicate_rows": int(df["text"].duplicated().sum()),
        "normalised_duplicate_rows": int(df["norm"].duplicated().sum()),
        "unique_normalised": int(df["norm"].nunique()),
        "fragment_counts": df["fragment"].value_counts().astype(int).to_dict(),
        "url_rows": int(df["text"].str.contains(prompt_utils.URL_RE).sum()),
    }

    # Overlap: how many validation / test rows also appear in train?
    train = set(df.loc[df.split == "train", "norm"])
    overlap = {}
    for split in ("validation", "test"):
        sub = df[df.split == split]
        real = sub[sub.fragment == "prompt"]
        overlap[split] = {
            "all_rows_in_train": float(sub["norm"].isin(train).mean()),
            "prompt_rows_in_train": float(real["norm"].isin(train).mean()),
        }
    R["audit"]["split_overlap"] = overlap
    return df


# --------------------------------------------------------------------------
# 3. Clean prompts
# --------------------------------------------------------------------------
def build_clean_prompts(df: pd.DataFrame) -> pd.DataFrame:
    prompts = df[df.fragment == "prompt"]
    c = prompts.drop_duplicates("norm").copy()
    c["content"] = c["text"].map(prompt_utils.content_text)
    c["n_words"] = c["text"].map(lambda t: len(prompt_utils.content_words(t)))
    c["params"] = c["text"].map(prompt_utils.params)
    c["has_param"] = c["params"].map(bool)
    c["aspect"] = c["text"].map(prompt_utils.aspect_ratio)
    c["has_weight"] = c["text"].str.contains("::", regex=False)
    c["artists_strict"] = c["text"].map(lambda t: prompt_utils.artists(t, "strict"))
    c["artists_lenient"] = c["text"].map(lambda t: prompt_utils.artists(t, "lenient"))
    c["boosters"] = c["content"].map(prompt_utils.boosters)
    R["flow"] = {
        "raw_rows": int(len(df)),
        "excluded_non_prompt": int((df.fragment != "prompt").sum()),
        "prompt_rows": int(len(prompts)),
        "excluded_duplicates": int(len(prompts) - len(c)),
        "clean_prompts": int(len(c)),
        "min_content_words": prompt_utils.MIN_CONTENT_WORDS,
    }
    return c


# --------------------------------------------------------------------------
# 4. RQ1 structure
# --------------------------------------------------------------------------
def rq1(c: pd.DataFrame):
    n = len(c)
    w = c["n_words"]
    param_counts = Counter(name for ps in c["params"] for name in {p for p, _ in ps})
    sep = np.select(
        [c["content"].str.contains(r"\|"), c["content"].str.contains(",")],
        ["pipe", "comma"], "none")
    R["rq1"] = {
        "words_median": float(w.median()),
        "words_q1": float(w.quantile(0.25)),
        "words_q3": float(w.quantile(0.75)),
        "words_mean": float(w.mean()),
        "words_sd": float(w.std()),
        "any_param_pct": 100 * float(c["has_param"].mean()),
        "param_pct": {k: 100 * v / n for k, v in param_counts.most_common()},
        "aspect_top": {k: int(v) for k, v in c["aspect"].value_counts().head(10).items()},
        "aspect_rows": int(c["aspect"].notna().sum()),
        "weight_pct": 100 * float(c["has_weight"].mean()),
        "separator_pct": {k: 100 * float(v) for k, v in
                          pd.Series(sep).value_counts(normalize=True).items()},
    }


# --------------------------------------------------------------------------
# 5. RQ2 artists and boosters
# --------------------------------------------------------------------------
def rq2(c: pd.DataFrame):
    n = len(c)
    lenient = Counter(a for names in c["artists_lenient"] for a in set(names))
    boost = Counter(b for bs in c["boosters"] for b in bs)
    R["rq2"] = {
        "artist_strict_pct": 100 * float(c["artists_strict"].map(bool).mean()),
        "artist_lenient_pct": 100 * float(c["artists_lenient"].map(bool).mean()),
        "artist_distinct_lenient": len(lenient),
        "artist_top": dict(lenient.most_common(15)),
        "booster_any_pct": 100 * float(c["boosters"].map(bool).mean()),
        "booster_pct": {k: 100 * v / n for k, v in boost.most_common(15)},
    }
    # "artstation" also matches inside "trending on artstation", so the two
    # rows of booster_pct overlap. booster_any_pct counts each prompt once.


# --------------------------------------------------------------------------
# 6. RQ3 topics
# --------------------------------------------------------------------------
def fit_topics(c: pd.DataFrame):
    """Fit the reference TF-IDF + NMF model. Returns (X, vocab, model)."""
    from sklearn.decomposition import NMF
    from sklearn.feature_extraction.text import TfidfVectorizer

    docs = c["content"].str.lower().tolist()
    vec = TfidfVectorizer(stop_words="english", min_df=20, max_df=0.5,
                          token_pattern=r"(?u)\b[a-z][a-z]{2,}\b")
    X = vec.fit_transform(docs)
    vocab = np.array(vec.get_feature_names_out())
    ref = NMF(n_components=N_TOPICS, init="nndsvd", random_state=SEED, max_iter=400).fit(X)
    return X, vocab, ref


def rq3(c: pd.DataFrame):
    from scipy.optimize import linear_sum_assignment
    from sklearn.decomposition import NMF

    X, vocab, ref = fit_topics(c)

    def top_words(model):
        return [list(vocab[np.argsort(row)[::-1][:TOP_WORDS]]) for row in model.components_]

    ref_topics = top_words(ref)
    # Documents with no in-vocabulary words get an all-zero topic vector, and
    # argmax would silently put them in topic 1. Count them as unassigned.
    W = ref.transform(X)
    assigned = W.sum(axis=1) > 0
    n_unassigned = int((~assigned).sum())
    share = np.bincount(W[assigned].argmax(axis=1), minlength=N_TOPICS) / X.shape[0]

    # Stability: refit on random 80% subsamples with a different seed, match
    # each run's topics to the reference (Hungarian on Jaccard), and report
    # how much the top words overlap. The refits use init="nndsvdar", which is
    # the reference's NNDSVD start with small random values in place of zeros,
    # so this measures sensitivity to the sample far more than to the starting
    # point. A fully random start (init="random") is a harsher test.
    rng = np.random.default_rng(SEED)
    jacc = np.zeros((N_STABILITY_RUNS, N_TOPICS))
    for r in range(N_STABILITY_RUNS):
        idx = rng.choice(X.shape[0], int(SUBSAMPLE_FRAC * X.shape[0]), replace=False)
        m = NMF(n_components=N_TOPICS, init="nndsvdar", random_state=SEED + r + 1,
                max_iter=400).fit(X[idx])
        run = top_words(m)
        sim = np.array([[len(set(a) & set(b)) / len(set(a) | set(b)) for b in run]
                        for a in ref_topics])
        rows, cols = linear_sum_assignment(-sim)
        jacc[r, rows] = sim[rows, cols]

    pd.DataFrame({
        "topic": range(1, N_TOPICS + 1),
        "share_pct": 100 * share,
        "stability_jaccard": jacc.mean(axis=0),
        "top_words": [" ".join(t) for t in ref_topics],
    }).to_csv(RESULTS / "topics.csv", index=False)

    R["rq3"] = {
        "vocab_size": int(len(vocab)),
        "n_topics": N_TOPICS,
        "unassigned_docs": n_unassigned,
        "unassigned_pct": 100 * n_unassigned / X.shape[0],
        "topics": [{"top_words": t, "share_pct": 100 * float(s), "jaccard": float(j)}
                   for t, s, j in zip(ref_topics, share, jacc.mean(axis=0))],
        "stability_mean_jaccard": float(jacc.mean()),
        "stability_runs": N_STABILITY_RUNS,
    }


# --------------------------------------------------------------------------
# 7. RQ4 hypothesis tests
# --------------------------------------------------------------------------
def rq4(c: pd.DataFrame):
    from scipy import stats

    # H1: prompts that use parameters are longer (content words).
    a = c.loc[c.has_param, "n_words"]
    b = c.loc[~c.has_param, "n_words"]
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rank_biserial = 2 * u / (len(a) * len(b)) - 1

    # H2: citing an artist is associated with using booster phrases.
    has_artist = c["artists_lenient"].map(bool)
    has_boost = c["boosters"].map(bool)
    table = pd.crosstab(has_artist, has_boost)
    chi2, p2, dof, _ = stats.chi2_contingency(table, correction=False)
    cramers_v = np.sqrt(chi2 / (table.values.sum() * (min(table.shape) - 1)))

    R["rq4"] = {
        "h1": {"n_param": int(len(a)), "n_no_param": int(len(b)),
               "median_param": float(a.median()), "median_no_param": float(b.median()),
               "U": float(u), "p": float(p), "rank_biserial": float(rank_biserial)},
        "h2": {"table": table.values.tolist(), "chi2": float(chi2), "dof": int(dof),
               "p": float(p2), "cramers_v": float(cramers_v),
               "boost_pct_if_artist": 100 * float(has_boost[has_artist].mean()),
               "boost_pct_if_no_artist": 100 * float(has_boost[~has_artist].mean())},
    }


# --------------------------------------------------------------------------
# Outputs
# --------------------------------------------------------------------------
def tex_escape(s: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("_", r"\_"), ("#", r"\#"), ("$", r"\$"), ("{", r"\{"), ("}", r"\}")):
        s = s.replace(a, b)
    return s


def write_tables():
    TABLES.mkdir(parents=True, exist_ok=True)
    f = R["flow"]
    rows = [("Raw rows (all splits)", f["raw_rows"]),
            ("\\quad excluded: not a prompt", f["excluded_non_prompt"]),
            ("Prompt rows", f["prompt_rows"]),
            ("\\quad excluded: duplicate", f["excluded_duplicates"]),
            ("Clean prompts", f["clean_prompts"])]
    body = "\n".join(f"{a} & {b:,} \\\\" for a, b in rows)
    (TABLES / "flow.tex").write_text(
        "\\begin{tabular}{lr}\n\\toprule\nStep & Rows \\\\\n\\midrule\n"
        + body + "\n\\bottomrule\n\\end{tabular}\n")

    frag = R["audit"]["fragment_counts"]
    total = R["raw"]["rows"]
    body = "\n".join(f"{tex_escape(k.replace('_', ' '))} & {v:,} & {100*v/total:.1f} \\\\"
                     for k, v in sorted(frag.items(), key=lambda kv: -kv[1]))
    (TABLES / "fragments.tex").write_text(
        "\\begin{tabular}{lrr}\n\\toprule\nRow type & Rows & \\% \\\\\n\\midrule\n"
        + body + "\n\\bottomrule\n\\end{tabular}\n")

    body = "\n".join(
        f"{i} & {t['share_pct']:.1f} & {t['jaccard']:.2f} & "
        f"{tex_escape(', '.join(t['top_words'][:6]))} \\\\"
        for i, t in enumerate(R["rq3"]["topics"], 1))
    (TABLES / "topics.tex").write_text(
        "\\begin{tabular}{rrrp{0.55\\columnwidth}}\n\\toprule\n"
        "\\# & \\% & $J$ & Top words \\\\\n\\midrule\n" + body
        + "\n\\bottomrule\n\\end{tabular}\n")

    # Every scalar as a LaTeX macro, so the paper's prose never goes stale:
    # \input{tables/numbers} then write \NCleanPrompts, \PctArtistLenient, ...
    a, q1, q2, q3, q4 = R["audit"], R["rq1"], R["rq2"], R["rq3"], R["rq4"]
    macros = {
        "NRaw": f"{R['raw']['rows']:,}",
        "NCleanPrompts": f"{f['clean_prompts']:,}",
        "NDupRows": f"{a['exact_duplicate_rows']:,}",
        "PctDupRows": f"{100*a['exact_duplicate_rows']/R['raw']['rows']:.1f}",
        "PctNonPrompt": f"{100*f['excluded_non_prompt']/f['raw_rows']:.1f}",
        "PctTestInTrain": f"{100*a['split_overlap']['test']['all_rows_in_train']:.1f}",
        "PctTestPromptsInTrain": f"{100*a['split_overlap']['test']['prompt_rows_in_train']:.1f}",
        "MedianChars": f"{a['chars_median']:.0f}",
        "MedianWords": f"{q1['words_median']:.0f}",
        "IQRWords": f"{q1['words_q1']:.0f}--{q1['words_q3']:.0f}",
        "PctAnyParam": f"{q1['any_param_pct']:.1f}",
        "PctAspect": f"{q1['param_pct'].get('aspect', 0):.1f}",
        "PctWeight": f"{q1['weight_pct']:.1f}",
        "PctArtistStrict": f"{q2['artist_strict_pct']:.1f}",
        "PctArtistLenient": f"{q2['artist_lenient_pct']:.1f}",
        "PctBoosterAny": f"{q2['booster_any_pct']:.1f}",
        "TopicJaccard": f"{q3['stability_mean_jaccard']:.2f}",
        "HOneRankBiserial": f"{q4['h1']['rank_biserial']:.2f}",
        "HTwoCramersV": f"{q4['h2']['cramers_v']:.2f}",
        "NPromptRows": f"{f['prompt_rows']:,}",
        "PctPromptRows": f"{100*f['prompt_rows']/f['raw_rows']:.1f}",
        "ArtistRuleRatio": f"{q2['artist_lenient_pct']/q2['artist_strict_pct']:.1f}",
        "NBoosters": str(len(prompt_utils.BOOSTERS)),
        "MedianWordsParam": f"{q4['h1']['median_param']:.0f}",
        "MedianWordsNoParam": f"{q4['h1']['median_no_param']:.0f}",
        "HTwoChi": f"{q4['h2']['chi2']:.1f}",
        "PctBoostIfArtist": f"{q4['h2']['boost_pct_if_artist']:.1f}",
        "PctBoostIfNoArtist": f"{q4['h2']['boost_pct_if_no_artist']:.1f}",
        "NTopicUnassigned": f"{q3['unassigned_docs']:,}",
        "PctTopicUnassigned": f"{q3['unassigned_pct']:.1f}",
        "MinTopicJaccard": f"{min(t['jaccard'] for t in q3['topics']):.2f}",
    }
    # Names quoted in the prose, so they follow the data too.
    for word, name in zip(("One", "Two"), q2["artist_top"]):
        macros[f"TopArtist{word}"] = tex_escape(name.title())
    for word, name in zip(("One", "Two", "Three"), q2["booster_pct"]):
        macros[f"TopBooster{word}"] = tex_escape(name)
    (TABLES / "numbers.tex").write_text(
        "% Generated by analysis/pipeline.py -- do not edit by hand.\n"
        + "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items()))


def write_figures(c: pd.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGURES.mkdir(parents=True, exist_ok=True)
    # No creation timestamp, so re-running without a change leaves git clean.
    PDF_META = {"CreationDate": None}
    SERIES, INK, INK2, GRID = "#2a78d6", "#0b0b0b", "#52514e", "#e4e3df"
    plt.rcParams.update({
        "font.family": "serif", "font.size": 8, "axes.edgecolor": INK2,
        "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.spines.top": False, "axes.spines.right": False,
        "pdf.fonttype": 42,
    })

    def hbar(data: dict, xlabel: str, name: str, fmt="{:.1f}"):
        labels = list(data)[::-1]
        values = [data[k] for k in labels]
        fig, ax = plt.subplots(figsize=(3.4, 0.18 * len(labels) + 0.6))
        ax.barh(labels, values, color=SERIES, height=0.7, edgecolor="white", linewidth=1)
        for y, v in enumerate(values):
            ax.text(v, y, " " + fmt.format(v), va="center", fontsize=7, color=INK2)
        ax.set_xlabel(xlabel)
        ax.xaxis.grid(True, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_xlim(0, max(values) * 1.18)
        fig.tight_layout()
        fig.savefig(FIGURES / f"{name}.pdf", metadata=PDF_META)
        plt.close(fig)

    hbar({k: v for k, v in list(R["rq1"]["param_pct"].items())[:10]},
         "% of clean prompts", "params")
    hbar(R["rq2"]["artist_top"], "Clean prompts citing name", "artists", fmt="{:,.0f}")
    hbar(R["rq2"]["booster_pct"], "% of clean prompts", "boosters")

    fig, ax = plt.subplots(figsize=(3.4, 1.9))
    w = c["n_words"].clip(upper=100)
    ax.hist(w, bins=range(prompt_utils.MIN_CONTENT_WORDS, 102, 2), color=SERIES,
            edgecolor="white", linewidth=0.5)
    ax.axvline(R["rq1"]["words_median"], color=INK, linewidth=1, linestyle="--")
    ax.text(R["rq1"]["words_median"], ax.get_ylim()[1] * 0.92,
            f"  median {R['rq1']['words_median']:.0f}", fontsize=7, color=INK)
    ax.set_xlabel("Content words per prompt (capped at 100)")
    ax.set_ylabel("Prompts")
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(FIGURES / "length.pdf", metadata=PDF_META)
    plt.close(fig)


def write_environment():
    import matplotlib, scipy, sklearn
    env = {"python": platform.python_version(), "platform": platform.platform(),
           "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
           "scikit-learn": sklearn.__version__, "matplotlib": matplotlib.__version__,
           "seed": SEED}
    try:
        import pyarrow
        env["pyarrow"] = pyarrow.__version__
    except ImportError:
        pass
    (RESULTS / "environment.json").write_text(json.dumps(env, indent=2) + "\n")


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    log("1 load");     df = load()
    log("2 audit");    df = audit(df)
    df[["split", "text"]].to_csv(HERE / "data" / "midjourney_prompts_all.csv", index=False)
    log("3 clean");   c = build_clean_prompts(df)
    log("4 rq1");      rq1(c)
    log("5 rq2");      rq2(c)
    log("6 rq3");      rq3(c)
    log("7 rq4");      rq4(c)
    log("outputs")
    (RESULTS / "results.json").write_text(json.dumps(R, indent=2) + "\n")
    write_tables()
    write_figures(c)
    write_environment()
    log("done")


if __name__ == "__main__":
    main()
