# AI-assisted analysis protocol (Part 1a)

The point of Part 1a is to see what a generative AI tool does with the same
dataset and the same research questions as our own pipeline, and to record
everything so the comparison is fair and someone else could repeat it.

## 1. Fix the setup before starting

Fill this in before the first session and copy it into the paper's
"AI tool setup" subsection.

| Item | Value |
|---|---|
| Tool and model | e.g. ChatGPT (GPT-5.x) with data analysis, or Claude.ai with the analysis tool. It must be able to run code on an uploaded file. |
| Plan / tier | |
| Date(s) of sessions | |
| Settings | memory off, custom instructions off, web search off, new chat each run |
| File uploaded | `analysis/data/midjourney_prompts_all.csv` (columns `split`, `text`; 246,381 rows) |
| File SHA-256 | `582e6d0977c554135f231e1e03d806535aa4755d61f3425c49ca6bfe28934806` |

Do **not** give the AI our rules from `analysis/prompt_utils.py` or our results.
We are testing what it does on its own.

Our own pipeline (Part 1b) was written with help from Claude Code. If you use
a Claude model for Part 1a as well, say so in the paper. Using a different
vendor (e.g. ChatGPT) keeps the two arms more independent.

## 2. Run the prompts

Paste each prompt exactly as written, in order, in one chat. Do not correct
or hint at anything between prompts; follow-up prompts are fixed in advance.
If the tool errors or times out, record it and send only `Please continue.`

**P0, open-ended (before any research question):**

> I have uploaded a dataset of text-to-image prompts collected from the
> Midjourney Discord server. Analyse this dataset and report your main
> findings.

**P1, data quality:**

> How clean is this dataset? Report how many rows are empty, duplicated, or
> are not real prompts, and whether rows in the validation and test splits
> also appear in the train split. Explain exactly how you decided what counts
> as "not a real prompt".

**P2, structure (RQ1):**

> Excluding rows that are not real prompts and removing duplicates, describe
> what a typical prompt looks like: its length in words, how often Midjourney
> parameters such as --ar, --no, --w/--h, --stop and --seed are used, and
> the most common aspect ratios.

**P3, artists and boosters (RQ2):**

> What share of prompts reference a named artist or "in the style of"
> someone? Which artists are named most often? What share use generic
> quality phrases such as "trending on artstation", "8k" or "octane render"?
> State the rule you used to detect each.

**P4, topics (RQ3):**

> Identify the main themes or topics in the prompts using a topic model.
> Report the topics with their top words and the share of prompts in each.
> How stable are these topics if the analysis is re-run?

**P5, hypothesis tests (RQ4):**

> Test two hypotheses and report the test, test statistic, p-value and an
> effect size for each: (H1) prompts that use at least one parameter are
> longer than prompts that use none; (H2) prompts that name an artist are
> more likely to use a quality phrase.

**P6, transparency:**

> Give me the complete code you ran for all of the above, in one block, so
> that I can reproduce your results.

## 3. Repeat for reproducibility

Run the whole sequence **three times**, each in a fresh chat with the same
settings (runs A, B, C). Run A is the main AI result; B and C show how much
the answers change from run to run.

## 4. Record everything

For each run, copy `runs/RUN_TEMPLATE.md` to `runs/run-A.md` (etc.) and paste
every prompt and the **full** response, including the code the tool ran and
any errors. Save the P6 code as `runs/run-A-code.py`. Do not edit or shorten
the responses. Shortened excerpts can go in the paper; the full log goes in
the appendix or as a supplementary file.

## 5. Score each run

Fill in `runs/scoring.csv` (one row per run per research question) using
these criteria, then check them against `analysis/results/results.json`.

| Criterion | What to record |
|---|---|
| Findings | The AI's headline number vs ours, and the difference |
| Rigor | Did it handle empties, fragments, duplicates, leakage? Report effect sizes, not just p? |
| Transparency | Did it state its rules? Did it show the code? Does the code match what it claimed? |
| Bias / errors | Invented numbers, overclaiming, unsupported causal language, ignored ethics |
| Reproducibility | Does its P6 code run and give the same numbers? Do runs A/B/C agree? |
