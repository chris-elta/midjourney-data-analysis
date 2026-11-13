# COMP 9200 Assignment 3

Dataset: [succinctly/midjourney-prompts](https://huggingface.co/datasets/succinctly/midjourney-prompts)
(246,381 Midjourney Discord prompts, one `text` column).

| Folder | What | Who |
|---|---|---|
| `analysis/` | Part 1b: our own pipeline | pair |
| `ai-analysis/` | Part 1a: AI-assisted analysis protocol and run logs | pair |
| `part1-paper/` | Part 1 IEEE paper | pair |
| `part2-methodology/` | Part 2 methodology draft for the proposal | individual |

## Re-run the pipeline

From this folder:

```sh
python3 -m pip install --target analysis/.deps pyarrow==14.0.2   # once
PYTHONPATH=analysis/.deps python3 analysis/fetch_data.py         # download + hash
PYTHONPATH=analysis/.deps python3 analysis/pipeline.py           # ~30 s
cd part1-paper && latexmk -pdf COMP9200_A3_Part1_Paper.tex
```

Other packages are pinned in `analysis/requirements.txt`. The pipeline writes
`analysis/results/`, `part1-paper/tables/` (including `numbers.tex`, the
macros used in the paper's text) and `part1-paper/figures/`. Never edit those
by hand; change `analysis/prompt_utils.py` or `analysis/pipeline.py` and re-run.

## What's left to do

1. **Part 1a:** follow `ai-analysis/PROTOCOL.md`: pick the tool, run P0–P6
   three times, log the runs in `ai-analysis/runs/`, fill in `scoring.csv`.
2. **Part 1 paper:** fill in every red `[TODO]`: AI tool setup, AI results,
   Table III's AI column, Discussion, Conclusion, abstract, appendices,
   partner details. Check every entry in `a3references.bib`.
3. **Validity check:** each partner labels the 100 prompts in
   `analysis/validity/handcheck.csv` on their own (columns `*_r1` / `*_r2`),
   then run `python3 analysis/validity_score.py` and rebuild the paper: it
writes precision, recall and Cohen's kappa to `part1-paper/tables/validity.tex`,
which Discussion > Validity uses (section 7 of `analysis/explore.ipynb` shows
the same numbers).
4. **Part 2:** write the methodology draft in
   `part2-methodology/` (skeleton only).

`analysis/explore.ipynb` shows example rows behind every cleaning step and
research question. It never writes the paper's numbers; run it with
*Restart & Run All* before submitting so its saved outputs are current.

## LaTeX setup

`texmf/` holds the IEEEtran class, bibliography style and other packages,
matched to the system TeX install. The root `.latexmkrc` puts it on the TeX
path, and each paper folder's `.latexmkrc` loads the root one, so
`latexmk -pdf` works from either paper folder.
