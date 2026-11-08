# Midjourney prompt analysis: responses

## Request 1

I have uploaded a dataset of text-to-image prompts collected from the Midjourney Discord server. Analyse this dataset and report your main findings.

### Response

## Main findings

The file [midjourney_prompts_all.csv](/home/elta/mj-ai-run-A/midjourney_prompts_all.csv) contains **246,381 rows**, split 90% train, 5% test and 5% validation. It has only two fields: `split` and `text`. The strongest finding is that the file is **not a clean collection of distinct, complete prompts**: it contains extensive repetition and many short fragments.

### 1. Repetition and fragments dominate

- **1,597 rows are empty.** Of all rows, only **65,398 texts are exactly distinct**, including the empty string. Thus, 73.5% of rows are additional occurrences of an exact duplicate.
- Among nonempty rows, **55.2% have five or fewer word-like tokens**; the median is three. This is a length measure, not a judgment that every short entry is invalid.
- Some entries are clearly parameter-like fragments rather than descriptive prompts: **14.3%** of nonempty rows consist solely of an aspect ratio, **5.5%** solely of a double-hyphen parameter, and **5.1%** solely of a number. For example, `16:9` occurs 12,470 times.
- Longer entries are repeated too: one descriptive text appears **736 times**. Repetition can therefore substantially change the apparent prevalence of themes and styles.

The file does not reveal whether fragments or duplicates arose during collection, export, or prompt submission.

### 2. The train/test split has substantial exact overlap

Of the **12,320 test rows, 10,239 (83.1%)** have text that also appears in training. Validation has a similar overlap: **10,365 of 12,318 rows (84.1%)**.

This is not only a short-fragment issue. Among test rows with at least six word-like tokens, **3,851 of 5,516 (69.8%)** also occur exactly in training. These overlaps make the existing splits unreliable for measuring generalization to unseen text; near-duplicates may add further leakage.

### 3. Longer distinct texts emphasize visual treatment

To reduce the influence of fragments and exact repetition, I also examined the **51,451 distinct nonempty texts with at least six word-like tokens**. This is a pragmatic filter, not a guarantee that every remaining row is a complete prompt.

| Literal phrase or word | Distinct longer texts | Share |
|---|---:|---:|
| `cinematic` | 6,205 | 12.1% |
| `style of` | 4,525 | 8.8% |
| `octane render` | 4,434 | 8.6% |
| `portrait` or `portraits` | 3,096 | 6.0% |
| `highly detailed` | 2,715 | 5.3% |
| `unreal engine` | 2,333 | 4.5% |
| `trending on artstation` | 2,125 | 4.1% |

These are **literal, overlapping matches**, not comprehensive topic categories. They suggest a strong use of cinematic, rendering, detail and artistic-reference language. The exact phrase `style of` appears in 8.8%; named-artist references are also visible, including `Craig Mullins` in 2.5% and `Peter Mohrbacher` in 1.9%.

### 4. Aspect ratios are common where explicitly specified

Among the distinct longer texts, **20,488** contain a recognizable `--ar` or `--aspect` ratio, including variants written with an en/em dash. Of those, **54.2% specify landscape**, **45.3% portrait**, and **0.6% square**. The most common exact ratios are **16:9** (6,714 texts) and **9:16** (2,463). This describes texts with an explicit recognizable ratio, not all generated images.

## Interpretation and recommended use

The dataset is useful for exploring *wording and prompt conventions*, but its row frequencies should not be treated as representative of Midjourney users or of successful image-generation practices. The file provides no timestamps, authors, images, outcomes or collection methodology, so it cannot establish trends over time, user demographics, or which prompts worked best.

For analysis or model evaluation, I would first investigate the fragment-producing pipeline, preserve both raw and cleaned versions, deduplicate, and create new splits **after** grouping exact and near-duplicate texts. Near-duplicate grouping is especially important because repeated prompts often differ only by a few modifiers.

## Request 2

How clean is this dataset? Report how many rows are empty, duplicated, or are not real prompts, and whether rows in the validation and test splits also appear in the train split. Explain exactly how you decided what counts as "not a real prompt".

### Response

## Overall assessment

The [dataset](/home/elta/mj-ai-run-A/midjourney_prompts_all.csv) is **quite noisy**. Of its 246,381 rows:

| Measure | Rows | Share of all rows |
|---|---:|---:|
| Empty | 1,597 | 0.65% |
| Nonempty, flagged as not a standalone descriptive prompt | 61,217 | 24.85% |
| Empty **or** flagged as non-prompt | 62,814 | 25.49% |
| Additional occurrences of an exact duplicate | 180,983 | 73.46% |

The duplicate figure means that, if one copy of each exact text were retained, 180,983 rows would be removed. Counting *every* row belonging to a duplicated group—including the first copy—gives **208,436 rows**. Duplicate counts include empty rows and can overlap with the non-prompt counts; they should not be added together.

## What I counted as “not a real prompt”

There is no ground-truth label for whether a row is a real prompt. I used a **conservative, reproducible proxy**: a nonempty row is flagged only if its entire text, apart from surrounding whitespace, is one of the following:

| Entire row consists of | Examples | Rows |
|---|---|---:|
| A numeric aspect ratio: digits, a colon, then digits | `16:9`, `2:3` | 34,993 |
| A number: digits, optionally followed by a decimal point and digits | `1920`, `0.5` | 12,467 |
| One or more parameter tokens, each optionally followed by one whitespace-delimited value | `--uplight`, `--ar 16:9` | 13,757 |
| A URL alone, starting with `http://` or `https://` | — | 0 |
| **Total nonempty flagged rows** | | **61,217** |

For the parameter rule, a token starts with `--`, `—` or `–`, followed by an ASCII letter and then letters, digits or hyphens. A value cannot itself begin with one of those parameter prefixes. Empty means the text is blank after trimming whitespace.

These are **not a definitive count of all invalid prompts**. For example, `render`, `style` and `field` were *not* flagged: a one-word entry could be an intentional prompt, although it could also be a fragment. There are **52,970 unflagged rows containing exactly one word-like token**, so the true number of incomplete or unhelpful rows could be considerably higher. Conversely, the rule calls a standalone parameter or ratio non-descriptive; it cannot establish what the person who submitted it intended.

## Do validation and test texts appear in training?

Yes. Comparing the **exact text**, including empty strings, against the training split:

| Split | Rows | Rows also appearing in train | Share |
|---|---:|---:|---:|
| Validation | 12,318 | 10,365 | 84.1% |
| Test | 12,320 | 10,239 | 83.1% |

The overlap remains substantial even after excluding empty rows and the non-prompt types defined above: **7,208 of 9,154 validation rows (78.7%)** and **7,199 of 9,275 test rows (77.6%)** occur exactly in training.

These figures count rows, not distinct texts. Exact matching also misses near-duplicates, so it likely understates related-text overlap. For a meaningful held-out evaluation, the data should be cleaned and grouped by exact—and preferably near—duplicate text *before* creating new splits.

## Request 3

Excluding rows that are not real prompts and removing duplicates, describe what a typical prompt looks like: its length in words, how often Midjourney parameters such as --ar, --no, --w/--h, --stop and --seed are used, and the most common aspect ratios.

### Response

Using the **same conservative non-prompt rule as before**, then removing exact duplicate texts across all splits, leaves **64,907 distinct rows**. This filter removes empty rows and standalone numbers, ratios, parameters and URLs, but it does not establish that every remaining row is a complete prompt.

## Length and wording

Counting whitespace-separated items—including parameter flags and their values—the median prompt is **12 words/items** and the mean is **15.9**. The middle half have **6–21 items**. Short entries remain: **5,127 (7.9%)** have only one whitespace-separated item.

A common pattern is a subject followed by visual or style modifiers, sometimes with a parameter. For example, an illustrative—not quoted—prompt might look like:

> a lighthouse on a rocky coast, cinematic lighting, highly detailed --ar 16:9

Among all 64,907 distinct rows, the literal word `cinematic` appears in **9.6%**, and the phrase `octane render` in **6.9%**. These are overlapping keyword matches, not a complete classification of prompt content.

## Parameter use

Counts are per distinct row, regardless of how often the parameter occurs within it. Detection includes `--` and en/em-dash variants.

| Parameter | Distinct rows | Share |
|---|---:|---:|
| Any recognizable parameter | 27,371 | 42.2% |
| `--ar` | 17,946 | 27.6% |
| `--aspect` | 2,716 | 4.2% |
| Either `--ar` or `--aspect` | 20,662 | 31.8% |
| `--no` | 2,343 | 3.6% |
| `--w` | 3,389 | 5.2% |
| `--h` | 3,402 | 5.2% |
| Both `--w` and `--h` | 2,943 | 4.5% |
| `--stop` | 738 | 1.1% |
| `--seed` | 166 | 0.3% |

## Most common aspect ratios

Among the **20,662 distinct rows** with a recognizable explicit `--ar` or `--aspect` ratio:

| Ratio | Rows | Share of rows with a ratio |
|---|---:|---:|
| 16:9 | 6,789 | 32.9% |
| 9:16 | 2,475 | 12.0% |
| 2:3 | 1,508 | 7.3% |
| 4:5 | 819 | 4.0% |
| 16:8 | 693 | 3.4% |
| 3:4 | 602 | 2.9% |

Ratios are reported **as written**, rather than reducing equivalent ratios. For the 19 rows with multiple recognized ratio specifications, I counted the first. These figures do not imply the aspect ratios used by rows without an explicit ratio.

Because the cleaning rule deliberately leaves ambiguous short entries in place, the typical length is sensitive to that choice. As a comparison, restricting the analysis further to distinct rows with at least six word-like tokens gives a median of **15 whitespace-separated items**.

## Request 4

What share of prompts reference a named artist or "in the style of" someone? Which artists are named most often? What share use generic quality phrases such as "trending on artstation", "8k" or "octane render"? State the rule you used to detect each.

### Response

Using the same cleaning rule and exact-text deduplication as before, the denominator is **64,907 distinct rows**. Matches below are counted once per row and are case-insensitive.

## Artist and style references

I found **8,786 rows (13.5%)** mentioning at least one of the 50 artist names or aliases listed below. Separately, **3,689 (5.7%)** contain the exact phrase `in the style of`. The two groups overlap in 1,435 rows; their union is **11,040 rows (17.0%)**.

**That 17.0% is a proxy, not the exact share referring to an artist.** The name list misses artists and spellings; a name can appear without requesting that artist’s style; and `in the style of` can refer to a studio, work or genre rather than a person.

### Most-mentioned names in the searched list

| Artist or alias | Distinct rows | Share |
|---|---:|---:|
| Craig Mullins | 1,283 | 2.0% |
| Peter Mohrbacher | 963 | 1.5% |
| Alphonse Mucha / Mucha | 817 | 1.3% |
| H. R. Giger / Giger | 678 | 1.0% |
| Mœbius / Moebius / Jean Giraud | 573 | 0.9% |
| James Jean | 516 | 0.8% |
| Artgerm | 515 | 0.8% |
| James Gurney | 423 | 0.7% |
| Ashley Wood | 401 | 0.6% |
| Zdzisław Beksiński / Beksinski | 392 | 0.6% |

These are the leaders **among the names searched**, not a guaranteed ranking of every artist in the dataset. Rows can name multiple artists.

**Detection rule.** I searched anywhere in each row for whole-word name matches, allowing whitespace between name components. The 50-name list comprised Craig Mullins, Peter Mohrbacher, Tsutomu Nihei, Floria Sigismondi, Robert Mapplethorpe, Ashley Wood, Hajime Sorayama, Sarah Morris, Annie Leibovitz, WLOP, Hokusai, Hayao Miyazaki, Ansel Adams, Joel Meyerowitz, Karel Thole, Alphonse Mucha, James Jean, Renato Muccillo, Artgerm, Thomas Kinkade, Katsuhiro Otomo, Jean-Honoré Fragonard, Harumi Hironaka, Charlie Bowater, Mœbius, Greg Rutkowski, Kilian Eng, Marc Simonetti, Gustave Doré, Beeple, Tom Bagshaw, Andrei Riabovitchev, Ross Tran, Yoshitaka Amano, Yoji Shinkawa, Tim Burton, Tim Walker, Wes Anderson, Norman Rockwell, Makoto Shinkai, Emil Melmoth, James Gurney, Syd Mead, Filip Hodas, Stefan Gesell, Jean-Michel Basquiat, Yousuf Karsh, H. R. Giger, Zdzisław Beksiński and Vincent van Gogh.

The search also included the aliases or variants shown in the table, plus `Alfons Mucha`, `Thomas Kindkade`, `Jean-Honore Fragonard`, `Gustave Dore`, `Basquiat`, `HR Giger`, `H.R. Giger`, `Zdzislaw Beksinski`, `Beksinkski` and `van Gogh`. The separate style-phrase search matched those four words in order, allowing whitespace between them; it did **not** check whether a person’s name followed.

## Generic quality and rendering phrases

| Literal phrase | Distinct rows | Share |
|---|---:|---:|
| `8k` | 5,915 | 9.1% |
| `octane render` | 4,452 | 6.9% |
| `trending on artstation` | 2,130 | 3.3% |
| **At least one of those three** | **9,948** | **15.3%** |

For context, `4k` occurs in **4.9%**, `highly detailed` in **4.2%**, and `unreal engine` in **3.6%**. Including these three additional phrases, **21.8%** contain at least one of the six.

**Detection rule.** Each term was matched literally, case-insensitively, with word boundaries and flexible whitespace between words. The union counts each row once even if it contains several terms. This measures the presence of these selected phrases—not image quality, and not every possible quality-related phrase.

## Request 5

Identify the main themes or topics in the prompts using a topic model. Report the topics with their top words and the share of prompts in each. How stable are these topics if the analysis is re-run?

### Response

## Topic-model results

I fitted a **10-topic non-negative matrix factorization (NMF)** model to the same cleaned, exact-deduplicated dataset used previously. The model assigned each text to its highest-weight topic. Labels below are my summaries of the top-weighted words; they are not labels supplied with the data.

| Interpreted topic | Top words | Share |
|---|---|---:|
| Cinematic lighting and scenes | cinematic, lighting, dark, light, epic, city, high, dramatic | 21.0% |
| Rendering and realism | render, realistic, octane, hyper, unreal, engine, ultra, photo | 13.7% |
| Black-and-white imagery | black, white, photo, background, red, ink, paper, photograph | 12.8% |
| Style and animation references | style, anime, ghibli, pixar, poster, design, mullins, basquiat | 11.8% |
| Portraits and characters | portrait, beautiful, artstation, character, face, girl, trending, wood | 11.1% |
| Painting | painting, oil, matte, abstract, beautiful, battle, hyperrealistic, cgsociety | 9.3% |
| Detail and intricacy | detailed, highly, intricate, hyper, cgsociety, alien, insanely, ornate | 8.8% |
| Concept and digital art | art, concept, vector, fantasy, digital, psychedelic, circa, pulp | 8.5% |
| Clay and sculpture | clay, shot, length, cute, race, sculpture, man, king | 2.1% |
| Artwork and names | artwork, van, john, peter, mike, robert, david, shinkawa | 0.9% |

The shares use **61,246 modelled texts** as their denominator. Of the 64,907 cleaned, distinct rows, **3,661 (5.6%)** had no retained vocabulary and could not be assigned a topic. The table therefore describes the modelled subset, not every row.

A notable result is that many clusters describe **aesthetic instructions or prompting conventions**, rather than subjects such as people or places. The “artwork and names” cluster is particularly difficult to interpret reliably.

## How stable are they?

I reran the model twice with different random initializations, keeping the data and settings fixed. After matching topics across runs by their word-weight similarity:

- Mean matched-topic cosine similarity was **0.88** for one rerun and **0.76** for the other; higher is more similar.
- The share of texts assigned to the corresponding topic was **81.2%** and **60.5%**, respectively.
- Some themes, including painting and concept art, remained recognizable. Others split, merged or disappeared: for example, the small clay topic in the first run did not have a close one-to-one match in either rerun.

The broad themes are therefore useful as an exploratory summary, but the **individual shares and exact topic boundaries are not highly stable**. These reruns test initialization sensitivity only—not changes to the number of topics, preprocessing, or the sampled dataset.

## Method

The model used English stop-word removal and TF–IDF-weighted words. I removed URLs and parameter flags, excluded numeric tokens, and retained terms appearing in at least 20 texts. The choice of ten topics was an exploratory setting, not a proven optimal number. Since the earlier cleaning rule is conservative, some fragments and near-duplicates also remain.

The [analysis script](/home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/topic_analysis.py) contains the preprocessing and all three runs.

## Request 6

Test two hypotheses and report the test, test statistic, p-value and an effect size for each: (H1) prompts that use at least one parameter are longer than prompts that use none; (H2) prompts that name an artist are more likely to use a quality phrase.

### Response

Both hypotheses are supported **within the analyzed dataset**, subject to the dependence and detection limitations below. I used the same **64,907 cleaned, exact-deduplicated texts** as in the previous answers.

## H1: Prompts with parameters are longer

Length is the number of whitespace-separated items, including parameter flags and values. A parameter is a recognizable flag beginning with `--`, `—` or `–`.

| Group | Texts | Median length | Mean length |
|---|---:|---:|---:|
| At least one parameter | 27,371 | 19 | 23.1 |
| No recognized parameter | 37,536 | 8 | 10.7 |

- **Test:** One-sided Mann–Whitney U test, with tie correction.
- **Statistic:** \(U = 820{,}121{,}638\).
- **p-value:** approximately \(1.7 \times 10^{-3677}\).
- **Effect size:** rank-biserial correlation **0.597**. Equivalently, a randomly selected parameter-containing text is longer than a randomly selected text without one with probability **79.8%**, counting ties as half.

Parameter syntax itself adds items. As a sensitivity check, I removed flags and one following value for common value-taking options: the medians were still **17 versus 8**, with rank-biserial correlation **0.486**. This parsing is approximate—for example, it does not remove every word of a multiword exclusion.

## H2: Artist-naming prompts more often use a quality phrase

“Names an artist” means a match to the **50-name-and-alias list from the previous answer**. “Quality phrase” means at least one of `trending on artstation`, `8k`, `octane render`, `highly detailed`, `4k`, or `unreal engine`.

| | Quality phrase | None of the six | Share with phrase |
|---|---:|---:|---:|
| Artist name detected | 3,502 | 5,284 | 39.9% |
| No listed artist detected | 10,617 | 45,504 | 18.9% |

- **Test:** Pearson chi-square test of independence, two-sided.
- **Statistic:** \(\chi^2(1) = 1{,}957.18\).
- **p-value:** approximately \(1.8 \times 10^{-427}\).
- **Effect size:** odds ratio **2.84**; the observed rates differ by **20.9 percentage points**.

The artist detector misses names outside its list and can match a name in a context that is not a style request. Similarly, the six phrases are only a subset of possible quality language.

## Interpretation

These are **associations, not causal findings**. Although exact duplicates were removed, near-duplicate prompts and shared templates remain, and the data lack author information. The tests’ p-values assume independent observations, so they should not be read as precise evidence about a broader population of Midjourney users.

The [reproducible test script](/home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/hypothesis_tests.py) includes the detection rules and calculations.

## Request 7

Give me the complete code you ran for all of the above, in one block, so that I can reproduce your results.

### Response

I originally used separate exploratory commands; the block below is a **consolidated, verified reproduction**, not a verbatim transcript of every exploratory command. Run it from the directory containing the CSV. I used Python 3.8, NumPy 1.24.4, SciPy 1.10.1 and scikit-learn 1.3.2.

**Correction:** I previously described 52,970 unflagged rows as having *exactly* one word-like token. That number has **at most one**; exactly 51,872 have one, and 1,098 have zero under the regex used.

```python
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
```

## Request 8

Save artifacts to this directory as run-A-(filename)

### Response

Saved and verified:

- [run-A-reproduce_all.py](./run-A-reproduce_all.py)
- [run-A-topic_analysis.py](./run-A-topic_analysis.py)
- [run-A-hypothesis_tests.py](./run-A-hypothesis_tests.py)

The existing [run-A.json](./run-A.json) was not changed.
