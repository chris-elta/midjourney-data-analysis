import os

# Set these before importing NumPy or scikit-learn.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import math
import re
import statistics
import warnings
from collections import Counter

import numpy as np
import scipy
import sklearn
from scipy import stats
from scipy.optimize import linear_sum_assignment
from sklearn.decomposition import NMF
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


CSV_PATH = "midjourney_prompts_all.csv"

RATIO_ONLY = re.compile(r"\s*\d+\s*:\s*\d+\s*")
NUMBER_ONLY = re.compile(r"\s*\d+(?:\.\d+)?\s*")
PARAM_ONLY = re.compile(
    r"\s*(?:(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)"
    r"(?:\s+(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)*\s*",
    re.I,
)
URL_ONLY = re.compile(r"\s*https?://\S+\s*", re.I)
WORDLIKE = re.compile(r"[a-z]+(?:['’][a-z]+)?|\d+", re.I)
PARAM = re.compile(r"(?<!\S)(?:--|[—–])([a-z][a-z0-9-]*)", re.I)
RATIO = re.compile(
    r"(?<!\S)(?:--|[—–])(?:ar|aspect)\s+(\d+)\s*:\s*(\d+)", re.I
)
URL = re.compile(r"https?://\S+", re.I)
PARAM_WITH_VALUE = re.compile(
    r"(?<!\S)(?:--|[—–])([a-z][a-z0-9-]*)"
    r"(?:\s+(?!(?:--|[—–]))(\S+))?",
    re.I,
)
VALUE_OPTIONS = {
    "ar", "aspect", "w", "h", "stop", "seed", "iw", "no", "style",
    "q", "quality", "s", "stylize", "v", "version", "chaos", "c",
}

# Each key is one artist; aliases are searched independently, then combined.
ARTISTS = {
    "Craig Mullins": ["craig mullins"],
    "Peter Mohrbacher": ["peter mohrbacher"],
    "Tsutomu Nihei": ["tsutomu nihei"],
    "Floria Sigismondi": ["floria sigismondi"],
    "Robert Mapplethorpe": ["robert mapplethorpe"],
    "Ashley Wood": ["ashley wood"],
    "Hajime Sorayama": ["hajime sorayama"],
    "Sarah Morris": ["sarah morris"],
    "Annie Leibovitz": ["annie leibovitz"],
    "WLOP": ["wlop"],
    "Hokusai": ["hokusai"],
    "Hayao Miyazaki": ["hayao miyazaki"],
    "Ansel Adams": ["ansel adams"],
    "Joel Meyerowitz": ["joel meyerowitz"],
    "Karel Thole": ["karel thole"],
    "Alphonse Mucha": ["alphonse mucha", "alfons mucha", "mucha"],
    "James Jean": ["james jean"],
    "Renato Muccillo": ["renato muccillo"],
    "Artgerm": ["artgerm"],
    "Thomas Kinkade": ["thomas kinkade", "thomas kindkade"],
    "Katsuhiro Otomo": ["katsuhiro otomo"],
    "Jean-Honoré Fragonard": ["jean-honoré fragonard", "jean-honore fragonard"],
    "Harumi Hironaka": ["harumi hironaka"],
    "Charlie Bowater": ["charlie bowater"],
    "Mœbius": ["mœbius", "moebius", "jean giraud"],
    "Greg Rutkowski": ["greg rutkowski"],
    "Kilian Eng": ["kilian eng"],
    "Marc Simonetti": ["marc simonetti"],
    "Gustave Doré": ["gustave dore", "gustave doré"],
    "Beeple": ["beeple"],
    "Tom Bagshaw": ["tom bagshaw"],
    "Andrei Riabovitchev": ["andrei riabovitchev"],
    "Ross Tran": ["ross tran"],
    "Yoshitaka Amano": ["yoshitaka amano"],
    "Yoji Shinkawa": ["yoji shinkawa"],
    "Tim Burton": ["tim burton"],
    "Tim Walker": ["tim walker"],
    "Wes Anderson": ["wes anderson"],
    "Norman Rockwell": ["norman rockwell"],
    "Makoto Shinkai": ["makoto shinkai"],
    "Emil Melmoth": ["emil melmoth"],
    "James Gurney": ["james gurney"],
    "Syd Mead": ["syd mead"],
    "Filip Hodas": ["filip hodas"],
    "Stefan Gesell": ["stefan gesell"],
    "Jean-Michel Basquiat": ["jean-michel basquiat", "basquiat"],
    "Yousuf Karsh": ["yousuf karsh"],
    "H. R. Giger": ["hr giger", "h.r. giger", "giger"],
    "Zdzisław Beksiński": [
        "zdzisław beksiński", "zdzislaw beksinski", "beksinski", "beksinkski"
    ],
    "Vincent van Gogh": ["vincent van gogh", "van gogh"],
}
QUALITY = [
    "trending on artstation", "8k", "octane render",
    "highly detailed", "4k", "unreal engine",
]


def classification(text):
    if not text.strip():
        return "empty"
    for label, pattern in (
        ("ratio", RATIO_ONLY),
        ("number", NUMBER_ONLY),
        ("parameter_only", PARAM_ONLY),
        ("url_only", URL_ONLY),
    ):
        if pattern.fullmatch(text):
            return label
    return "not_flagged"


def literal(text):
    return r"(?<!\w)" + r"\s+".join(re.escape(x) for x in text.split()) + r"(?!\w)"


def without_parameters(text):
    def replace(match):
        name, value = match.groups()
        return " " if value is None or name.lower() in VALUE_OPTIONS else " " + value
    return PARAM_WITH_VALUE.sub(replace, text)


def show_overlap(rows, label, predicate):
    subset = [r for r in rows if predicate(r["text"])]
    train = {r["text"] for r in subset if r["split"] == "train"}
    for split in ("validation", "test"):
        selected = [r["text"] for r in subset if r["split"] == split]
        unique = set(selected)
        print("OVERLAP", label, split, "rows", len(selected),
              "matching_rows", sum(t in train for t in selected),
              "unique", len(unique), "matching_unique", len(unique & train))


def length_test(lengths, group, label):
    x, y = lengths[group], lengths[~group]
    result = stats.mannwhitneyu(x, y, alternative="greater", method="asymptotic")
    ties = np.array(list(Counter(lengths).values()), dtype=np.float64)
    n1, n0 = len(x), len(y)
    n = n1 + n0
    variance = n1 * n0 / 12 * (n + 1 - np.sum(ties ** 3 - ties) / (n * (n - 1)))
    z = (result.statistic - n1 * n0 / 2 - 0.5) / math.sqrt(variance)
    superiority = result.statistic / (n1 * n0)
    print(label, "n", n1, n0, "means", x.mean(), y.mean(),
          "medians", np.median(x), np.median(y), "U", result.statistic,
          "log10_p", stats.norm.logsf(z) / math.log(10),
          "probability_superiority", superiority,
          "rank_biserial", 2 * superiority - 1)


with open(CSV_PATH, encoding="utf-8-sig", newline="") as file:
    rows = list(csv.DictReader(file))
texts = [r["text"] for r in rows]
nonempty = [t for t in texts if t.strip()]
clean = list(dict.fromkeys(t for t in texts if classification(t) == "not_flagged"))
print("VERSIONS", "numpy", np.__version__, "scipy", scipy.__version__,
      "scikit-learn", sklearn.__version__)
print("\nDATA QUALITY")
print("ROWS", len(rows), "SPLITS", Counter(r["split"] for r in rows))
print("CATEGORIES", Counter(classification(t) for t in texts))
counts = Counter(texts)
print("EXACT_UNIQUE", len(counts), "DUPLICATE_EXTRA", len(texts) - len(counts),
      "ROWS_IN_DUP_GROUPS", sum(v for v in counts.values() if v > 1),
      "DUPLICATE_GROUPS", sum(v > 1 for v in counts.values()))
normalized = Counter(re.sub(r"\s+", " ", t.strip().casefold()) for t in texts)
print("NORMALIZED_UNIQUE", len(normalized), "DUPLICATE_EXTRA", len(texts) - len(normalized))
print("TOP_REPEATED", counts.most_common(10))
nonempty_counts = Counter(nonempty)
print("NONEMPTY", len(nonempty), "EXACT_UNIQUE", len(nonempty_counts),
      "DUPLICATE_EXTRA", len(nonempty) - len(nonempty_counts))
word_lengths = sorted(len(WORDLIKE.findall(t)) for t in nonempty)
print("NONEMPTY_WORDLIKE", "mean", statistics.mean(word_lengths),
      "median", statistics.median(word_lengths),
      "p10", word_lengths[int(.1 * (len(word_lengths) - 1))],
      "p90", word_lengths[int(.9 * (len(word_lengths) - 1))],
      "at_most_five", sum(n <= 5 for n in word_lengths))
char_lengths = sorted(len(t) for t in nonempty)
print("NONEMPTY_CHARS", "mean", statistics.mean(char_lengths),
      "median", statistics.median(char_lengths),
      "p90", char_lengths[int(.9 * (len(char_lengths) - 1))])
long_rows = [t for t in nonempty if len(WORDLIKE.findall(t)) >= 6]
print("LONG_ROWS", len(long_rows), "TOP_REPEATED", Counter(long_rows).most_common(10))
not_flagged_rows = [t for t in texts if classification(t) == "not_flagged"]
print("NOT_FLAGGED_ONE_WORDLIKE",
      sum(len(WORDLIKE.findall(t)) == 1 for t in not_flagged_rows),
      "AT_MOST_ONE_WORDLIKE",
      sum(len(WORDLIKE.findall(t)) <= 1 for t in not_flagged_rows))
show_overlap(rows, "all", lambda t: True)
show_overlap(rows, "nonempty", lambda t: bool(t.strip()))
show_overlap(rows, "not_flagged", lambda t: classification(t) == "not_flagged")
show_overlap(rows, "six_wordlike", lambda t: bool(t.strip()) and len(WORDLIKE.findall(t)) >= 6)

print("\nCLEANED DISTINCT TEXTS", len(clean))
lengths = sorted(len(t.split()) for t in clean)
print("WHITESPACE_LENGTH", "mean", statistics.mean(lengths),
      "median", statistics.median(lengths),
      "p25", lengths[int(.25 * (len(lengths) - 1))],
      "p75", lengths[int(.75 * (len(lengths) - 1))],
      "one_item", sum(n == 1 for n in lengths))
long = [t for t in clean if len(WORDLIKE.findall(t)) >= 6]
print("SIX_WORDLIKE", len(long), "median_whitespace_length",
      statistics.median(len(t.split()) for t in long))
descriptive_patterns = {
    "cinematic": r"\bcinematic\b",
    "style of": r"\bstyle\s+of\b",
    "octane render": r"\boctane\s+render\b",
    "portrait(s)": r"\bportraits?\b",
    "highly detailed": r"\bhighly\s+detailed\b",
    "unreal engine": r"\bunreal\s+engine\b",
    "trending on artstation": r"\btrending\s+on\s+artstation\b",
    "photorealistic": r"\bphotorealistic\b",
    "Craig Mullins": r"\bcraig\s+mullins\b",
    "Peter Mohrbacher": r"\bpeter\s+mohrbacher\b",
}
for label, selected in (("clean", clean), ("six_wordlike", long)):
    print("DESCRIPTIVE", label, {
        name: sum(bool(re.search(pattern, t, re.I)) for t in selected)
        for name, pattern in descriptive_patterns.items()
    })
param_sets = [{x.lower() for x in PARAM.findall(t)} for t in clean]
param_counts = Counter()
for parameters in param_sets:
    param_counts.update(parameters)
print("PARAMETERS", param_counts.most_common())
print("ANY_PARAMETER", sum(bool(p) for p in param_sets),
      "W_OR_H", sum(bool({"w", "h"} & p) for p in param_sets),
      "W_AND_H", sum({"w", "h"} <= p for p in param_sets))
ratios = Counter()
orientations = Counter()
multiple = 0
for text in clean:
    matches = [(int(a), int(b)) for a, b in RATIO.findall(text)
               if int(a) > 0 and int(b) > 0]
    if matches:
        multiple += len(matches) > 1
        a, b = matches[0]
        ratios[f"{a}:{b}"] += 1
        orientations["landscape" if a > b else "portrait" if a < b else "square"] += 1
print("ASPECT_RATIOS", "rows", sum(ratios.values()), "multiple_rows", multiple,
      "orientation", orientations, "top", ratios.most_common(20))

print("\nARTISTS AND QUALITY PHRASES")
artist_patterns = {
    name: re.compile("|".join(literal(s) for s in aliases), re.I)
    for name, aliases in ARTISTS.items()
}
artist_matches = {
    name: {i for i, t in enumerate(clean) if pattern.search(t)}
    for name, pattern in artist_patterns.items()
}
any_artist = set().union(*artist_matches.values())
style_pattern = re.compile(r"\bin\s+the\s+style\s+of\b", re.I)
style = {i for i, t in enumerate(clean) if style_pattern.search(t)}
print("ARTISTS", len(any_artist), "STYLE_PHRASE", len(style),
      "BOTH", len(any_artist & style), "UNION", len(any_artist | style))
print("ARTIST_COUNTS", sorted(
    ((name, len(found)) for name, found in artist_matches.items()),
    key=lambda item: item[1], reverse=True,
))
quality_sets = {
    phrase: {i for i, t in enumerate(clean) if re.search(literal(phrase), t, re.I)}
    for phrase in QUALITY
}
print("QUALITY_COUNTS", {name: len(found) for name, found in quality_sets.items()})
print("QUALITY_FIRST_THREE_UNION",
      len(set().union(*(quality_sets[x] for x in QUALITY[:3]))))
any_quality = set().union(*quality_sets.values())
print("QUALITY_ALL_SIX_UNION", len(any_quality))

print("\nTOPIC MODEL")
vectorizer = TfidfVectorizer(
    lowercase=True, stop_words="english", token_pattern=r"(?u)\b[a-zA-Z]{3,}\b",
    min_df=20, max_df=0.6, max_features=8000, sublinear_tf=True,
)
matrix = vectorizer.fit_transform(without_parameters(URL.sub(" ", t)) for t in clean)
nonzero = np.asarray(matrix.getnnz(axis=1)).ravel() > 0
matrix = matrix[nonzero]
terms = vectorizer.get_feature_names_out()
print("MODELED", matrix.shape[0], "NO_FEATURES", int((~nonzero).sum()),
      "VOCAB", len(terms))
models = []
for seed in (0, 1, 2):
    model = NMF(n_components=10, init="random", random_state=seed,
                max_iter=500, tol=1e-4)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        weights = model.fit_transform(matrix)
    assignment = weights.argmax(axis=1)
    models.append((model.components_, assignment))
    print("FIT", seed, "iterations", model.n_iter_, "error", model.reconstruction_err_,
          "warnings", [str(w.message) for w in caught])
    for i, component in enumerate(model.components_):
        top = component.argsort()[-12:][::-1]
        print("TOPIC", seed, i, "count", int((assignment == i).sum()),
              "words", ",".join(terms[top]))

reference, reference_assignment = models[0]
for seed, (components, assignment) in zip((1, 2), models[1:]):
    similarity = cosine_similarity(reference, components)
    old, new = linear_sum_assignment(-similarity)
    mapping = np.empty(10, dtype=int)
    mapping[new] = old
    scores = similarity[old, new]
    jaccards = []
    for i, j in zip(old, new):
        left, right = set(reference[i].argsort()[-10:]), set(components[j].argsort()[-10:])
        jaccards.append(len(left & right) / len(left | right))
    print("STABILITY", seed, "mean_cosine", np.mean(scores),
          "min_cosine", np.min(scores), "mean_top10_jaccard", np.mean(jaccards),
          "min_top10_jaccard", np.min(jaccards),
          "assignment_agreement", np.mean(reference_assignment == mapping[assignment]))
    for i, j, score, jac in zip(old, new, scores, jaccards):
        print("MATCH", seed, int(i), int(j), "cosine", score, "jaccard", jac,
              "reference_share", np.mean(reference_assignment == i),
              "rerun_share", np.mean(assignment == j))

print("\nHYPOTHESIS TESTS")
parameter_group = np.array([bool(p) for p in param_sets])
length_test(np.array([len(t.split()) for t in clean]), parameter_group, "H1_FULL")
length_test(np.array([len(without_parameters(t).split()) for t in clean]),
            parameter_group, "H1_WITHOUT_OPTIONS")
artist_group = np.array([i in any_artist for i in range(len(clean))])
quality_group = np.array([i in any_quality for i in range(len(clean))])
a = int(np.sum(artist_group & quality_group))
b = int(np.sum(artist_group & ~quality_group))
c = int(np.sum(~artist_group & quality_group))
d = int(np.sum(~artist_group & ~quality_group))
chi2, p, dof, expected = stats.chi2_contingency([[a, b], [c, d]], correction=False)
odds_ratio = a * d / (b * c)
se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
interval = [math.exp(math.log(odds_ratio) + sign * 1.96 * se) for sign in (-1, 1)]
log10p = (math.log(2) + stats.norm.logsf(math.sqrt(chi2))) / math.log(10)
print("H2_TABLE", [[a, b], [c, d]], "chi2", chi2, "df", dof,
      "log10_p", log10p, "odds_ratio", odds_ratio, "or_95ci", interval,
      "rates", a / (a + b), c / (c + d),
      "risk_difference", a / (a + b) - c / (c + d),
      "risk_ratio", (a / (a + b)) / (c / (c + d)))
