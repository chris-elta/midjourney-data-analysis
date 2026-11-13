"""Score the hand check (Part 1 validity) and write the paper's macros.

Usage (from the repo root, once both raters have labelled):
    python3 analysis/validity_score.py

Reads  analysis/validity/handcheck.csv        (artist_r1/r2, booster_r1/r2,
                                                optional artist_final/booster_final)
       analysis/validity/handcheck_rules.csv  (what each pipeline rule said)
Writes part1-paper/tables/validity.tex        (\\Val... macros used in Discussion)

The reference labels are the agreed final labels when they exist for every
row, otherwise rater 1's labels. Final labels come from *_final columns in the
sheet, or from handcheck_disagreements.csv (the prompts where the raters
disagreed, settled by discussion); prompts both raters agree on keep that label. Cohen's kappa compares rater 1 and
rater 2. Same definitions as section 7 of explore.ipynb; standard library only.
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHEET = HERE / "validity" / "handcheck.csv"
RULES = HERE / "validity" / "handcheck_rules.csv"
DISAGREE = HERE / "validity" / "handcheck_disagreements.csv"
OUT = HERE.parent / "part1-paper" / "tables" / "validity.tex"


def column(rows, name):
    """0/1 values of a column, or None unless every row has one."""
    vals = [r.get(name, "").strip() for r in rows]
    if not all(v in ("0", "1") for v in vals):
        return None
    return [int(v) for v in vals]


def precision_recall(truth, pred):
    tp = sum(t and p for t, p in zip(truth, pred))
    fp = sum((not t) and p for t, p in zip(truth, pred))
    fn = sum(t and not p for t, p in zip(truth, pred))
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    return prec, rec


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def kappa_word(k):
    # Landis and Koch (1977) bands.
    # Use the value as printed (two decimals), so 0.60 reads "moderate".
    k = round(k, 2)
    for limit, word in ((0, "poor"), (0.20, "slight"), (0.40, "fair"),
                        (0.60, "moderate"), (0.80, "substantial")):
        if k <= limit:
            return word
    return "almost perfect"


def main():
    sheet = list(csv.DictReader(open(SHEET, encoding="utf-8", newline="")))
    rules = {r["row_id"]: r for r in csv.DictReader(open(RULES, encoding="utf-8", newline=""))}
    rows = [dict(r, **rules[r["row_id"]]) for r in sheet]
    if DISAGREE.exists():
        settled = {d["row_id"]: d for d in
                   csv.DictReader(open(DISAGREE, encoding="utf-8", newline=""))}
        for r in rows:
            for concept in ("artist", "booster"):
                if r.get(concept + "_final", "").strip():
                    continue
                d = settled.get(r["row_id"])
                if d is not None:
                    r[concept + "_final"] = d[concept + "_final"].strip()
                elif r[concept + "_r1"] == r[concept + "_r2"]:
                    r[concept + "_final"] = r[concept + "_r1"]
    n = len(rows)

    macros = {"ValN": str(n)}
    report = []
    for concept, rule_cols in (("artist", ("rule_artist_strict", "rule_artist_lenient")),
                               ("booster", ("rule_booster",))):
        r1, r2 = column(rows, concept + "_r1"), column(rows, concept + "_r2")
        final = column(rows, concept + "_final")
        if r1 is None:
            sys.exit(f"{concept}_r1 is not filled in for every row of {SHEET.name}")
        ref = final if final is not None else r1
        macros["ValReference"] = ("the agreed labels" if final is not None
                                  else "rater~1's labels")
        cap = concept.capitalize()
        macros[f"ValHuman{cap}Pct"] = f"{100 * sum(ref) / n:.0f}"
        if r2 is not None:
            k = kappa(r1, r2)
            macros[f"ValKappa{cap}"] = f"{k:.2f}"
            macros[f"ValKappa{cap}Word"] = kappa_word(k)
            macros[f"ValAgree{cap}"] = str(sum(x == y for x, y in zip(r1, r2)))
            report.append(f"{concept}: kappa {k:.2f} ({kappa_word(k)}), "
                          f"raters agree on {macros[f'ValAgree{cap}']}/{n}")
        else:
            for m in ("ValKappa", "ValAgree"):
                macros[f"{m}{cap}"] = "\\todo{rater 2}"
            macros[f"ValKappa{cap}Word"] = "\\todo{rater 2}"
            report.append(f"{concept}: rater 2 not complete, no kappa yet")
        for rc in rule_cols:
            pred = [int(r[rc]) for r in rows]
            p, rcl = precision_recall(ref, pred)
            name = {"rule_artist_strict": "Strict", "rule_artist_lenient": "Lenient",
                    "rule_booster": "Booster"}[rc]
            macros[f"ValPrec{name}"] = f"{p:.2f}"
            macros[f"ValRec{name}"] = f"{rcl:.2f}"
            report.append(f"  {rc:22s} flags {sum(pred):3d}  precision {p:.2f}  recall {rcl:.2f}")

    OUT.write_text("% Generated by analysis/validity_score.py -- do not edit by hand.\n"
                   + "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items()),
                   encoding="utf-8")
    print(f"reference: {macros['ValReference']}  (n={n})")
    print("\n".join(report))
    print("wrote", OUT.relative_to(HERE.parent))


if __name__ == "__main__":
    main()
