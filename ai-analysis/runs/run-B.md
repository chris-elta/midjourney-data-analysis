# AI run B (Claude)

- Tool / model: Claude Code extension in VS Code (version 2.1.322); model `claude-opus-5-5`, effort medium (recorded in the log)
- Date and time: 2026-11-11, 06:11 to 07:42 UTC
- Settings: new chat; memory, custom instructions and web search off as stated by the operator (the log shows no web search or web fetch calls)
- File uploaded or folder opened: folder `mj-ai-run-B` holding only `midjourney_prompts_all.csv` (Windows CRLF copy, SHA-256 0ba14bf7...05d9de; same content as the LF file 582e6d09...4806)
- Chat share link or export file: [run-B.jsonl](./run-B.jsonl) (Claude Code session log; account email and account IDs redacted, otherwise unchanged)

This run used a different tool from run A (GitHub Copilot, GPT). It is kept as a second AI tool, not as a repeat of run A.

All seven prompts were sent in order, verbatim, in one session.

The text below was extracted from the session log without editing: each prompt, then every text message the tool wrote in reply, in order (progress notes first, final answer last). Tool commands and their outputs are in run-B.jsonl.

## P0

**Request time:** 2026-11-11T06:11:48.498Z

**Prompt:**

> I have uploaded a dataset of text-to-image prompts collected from the Midjourney Discord server. Analyse this dataset and report your main findings.

**Response:**

I'll start by inspecting the dataset's structure and size.

---

The data has lots of short fragments ("16:9", "render") alongside full prompts, which matters for the analysis. I'll write a script to profile it.

---

Pandas is broken in this Python install, so I'll use the standard library instead of changing their environment.

---

Key early signal: about half the rows are single-word fragments and ~73% of rows are exact duplicates. Next I'll quantify split leakage and analyse the content of the real prompts.

---

Prompts are dominated by "quality booster" keywords and a small set of artists. One more check: what are the single-word fragment rows, and is there any ordering or structure I can infer from them?

---

I analysed all 246,381 rows. **The main finding is about data quality: once you remove fragments and duplicates, only about 56,000 of those rows are distinct, usable prompts (≈23%).**

## 1. Data quality

| Issue | Size |
|---|---|
| Rows with a single word or less | **50%** (e.g. `16:9`, `--uplight`, `render`, `nouveau`, `field`) |
| Rows that are only an aspect ratio (`16:9`, `9:16`, …) | 14% |
| Rows that are only a number (`1920`, `1080`) | 5% |
| Empty rows | 1,597 |
| Exact duplicate rows | **73%** (only 65,398 distinct texts) |
| Distinct prompts with 4+ words | **~56,000** |

- **The fragments are leftover tails of real prompts.** 99% of the 300 most common fragments also appear inside full prompts. For example, `nouveau` is from "art nouveau", `field` from "depth of field", and `16:9` is the value of `--ar 16:9`. This looks like the prompt-extraction step split some messages on spaces or parameters. The rows are also shuffled, so the pieces can't be put back together.
- **Heavy repetition.** Users re-ran the same or slightly changed prompts many times. One prompt ("cute furry monster in Pixar with star, colorful, volumetric lighting, 4k, photorealistic") appears 736 times, and several close variants add hundreds more.
- **The train/test/validation split leaks.** About 83% of test rows and 84% of validation rows also appear word-for-word in train, and 69% of the test prompts with 4+ words do too. Any model evaluated on these splits will look much better than it really is.

## 2. What the real prompts look like (~56k distinct prompts)

- **Length:** median 14 words. 10% run past 36 words, and the longest is 353 words. Most are comma-separated keyword lists rather than sentences.
- **Parameters:** about half the prompts use Midjourney flags.
  - `--ar` (33%) is by far the most common, followed by `--w`/`--h` (6%), `--uplight` (5.5%), `--aspect` (5%), `--no` (4.5%), and `--stop`, `--wallpaper`, `--test`, `--hd`.
  - 7% write the em-dash `—ar` instead of `--ar`, which is what phones and autocorrect produce.
- **Aspect ratios:** 16:9 dominates (33% of the prompts that set one), then 9:16 (12%), then 2:3 and 4:5. Landscape and wallpaper formats win clearly.
- **Era:** there are no `--v` version flags at all, while `--test`, `--uplight` and `--hd` are present. That points to the 2022 beta period of Midjourney (v1–v3).

## 3. Style and content

- **Generic "quality booster" words dominate:**
  - "realistic" (17%), "detailed" (15.5%), "cinematic" (11%), "8k" (10.5%)
  - "artstation" (9%), "octane render" (8%), "unreal engine" (4%), "trending on artstation" (4%)
- **Popular genres:** fantasy, cyberpunk, horror/gothic, steampunk, sci-fi and dystopian. Photography terms ("35mm", "photograph", "portrait") are also common.
- **Artist names are used heavily, and the list is concentrated.** The most frequent are Craig Mullins (~1,300 prompts), Peter Mohrbacher (~960), Miyazaki/Studio Ghibli (~700), H.R. Giger (~680), Monet, James Jean, Artgerm, Moebius, James Gurney, Ross Tran, Alphonse Mucha and Greg Rutkowski. Living illustrators make up a large share of these, which is relevant to the copyright debate around style prompting.
- **Pop culture and public figures appear often:** Star Wars (165), Batman (136), Trump (113), Biden (100), Darth Vader (86), Putin (57).
- **There is evidence of a content filter.** "nude" and "naked" never appear, and "sexy" appears only twice, which matches Midjourney's banned-word list at the time. Violence is rare but present ("blood" 59, "gore" 12).
- **Mostly English:** fewer than 200 distinct texts use CJK or Cyrillic script.

## Recommendations if you use this data
1. Drop rows with fewer than about 4 words, and drop rows that are only a ratio, number or URL.
2. Remove duplicates, ideally also after stripping `--` parameters and punctuation, which brings it down to about 53,000.
3. Rebuild the train/test/validation split from the cleaned, de-duplicated set so no prompt appears in more than one split.

I did all of this in plain Python because pandas is broken in your Python install (it's missing `dateutil`); I didn't change your environment. I can also turn these findings into a shareable page with charts if you'd like.

## P1

**Request time:** 2026-11-11T06:16:13.738Z

**Prompt:**

> How clean is this dataset? Report how many rows are empty, duplicated, or are not real prompts, and whether rows in the validation and test splits also appear in the train split. Explain exactly how you decided what counts as "not a real prompt".

**Response:**

I'll redo this with explicit, mutually exclusive rules so every row lands in exactly one bucket, then recount duplicates and split overlap with those rules.

---

One of my evidence checks was flawed: 3-word rows were being matched against themselves. I'll fix it and look at what 2- and 3-word rows actually contain before settling the cut-off.

---

Classification is settled. One last number: how many lone-word rows do *not* appear inside any longer prompt. That sets how uncertain the fragment bucket is.

---

**The dataset is not clean. Only about half the rows (123,867, or 50.3%) are real prompts, those collapse to 59,733 distinct prompts, and about two-thirds of the validation and test prompts also appear word-for-word in train.**

## Row breakdown (246,381 rows)

Each row is put in exactly one bucket, checked in this order:

| Bucket | Rows | Share |
|---|---:|---:|
| Empty or whitespace only | 1,597 | 0.6% |
| Image URL only (`<https://s.mj.run/...>`) | 1,077 | 0.4% |
| Discord user mention only (`@leekent13`) | 66 | <0.1% |
| Parameters or numbers only (`16:9`, `--uplight`, `1920`) | 63,172 | 25.6% |
| A single word alone on the row (`render`, `dof`, `field`) | 56,602 | 23.0% |
| **Not a real prompt (total)** | **122,514** | **49.7%** |
| **Real prompt** | **123,867** | **50.3%** |

The real-prompt count includes two borderline groups that I kept: 3,426 two-word prompts (e.g. "frog sticker") and 284 one-word prompts with parameters (e.g. "Jazz --ar 16:8").

## How I decided what is "not a real prompt"

I split each row on spaces and removed any word that carries no image description:
- a parameter flag: `--ar`, `—ar`, `--uplight`
- a number, ratio or weight: `1920`, `16:9`, `0.5`, `::0.75`
- an image URL or a Discord @mention
- the word `/imagine`

Then the rules were:
1. **Empty:** nothing but whitespace.
2. **URL only / mention only:** every word is a URL, or every word is a mention.
3. **Parameters or numbers only:** no word containing a letter is left after the removal. These are settings with nothing to draw.
4. **Single-word fragment:** the row is one word with nothing else on it. This is the only rule that involves judgment, and I tested it:
   - 96.7% of these rows (54,740 of 56,602) appear inside a longer prompt elsewhere in the data, such as `nouveau` from "art nouveau" and `field` from "depth of field". They are leftover pieces of prompts that were split badly, not prompts someone typed.
   - The other 1,862 rows are mostly junk too (`<--uplight`, `asdfghjkl`, `forms:1`). At most about 1,900 rows here might be real one-word prompts, which is under 1% of the dataset.
5. **Everything else is a real prompt.** I deliberately kept two-word rows. Only 20% of them appear inside longer prompts, and samples look like real short requests ("nautilus shell", "Anthropomorphic walrus").

This replaces the "fewer than 4 words" cut-off I used in my first answer. That cut-off was too strict and threw out real short prompts, which is why the distinct-prompt count rose from about 56,000 to 59,733.

## Duplicates

- **Across all rows:** 180,983 rows (73.5%) repeat a text that already appeared, leaving only 65,398 distinct texts. Most of these repeats are non-prompt rows, which shrink from 122,514 rows to 5,665 distinct values.
- **Among real prompts:** 64,134 of 123,867 prompt rows (51.8%) are exact repeats, leaving 59,733 distinct prompts. Ignoring case and spacing removes only 45 more (59,688).
- The most repeated prompt ("cute furry monster in Pixar with star…") appears 736 times.

## Do validation and test rows also appear in train?

Yes, heavily. "In train" here means the exact same text appears somewhere in the train split.

| | Validation | Test |
|---|---:|---:|
| All rows that also appear in train | 10,365 / 12,318 (84.1%) | 10,239 / 12,320 (83.1%) |
| Prompt rows that also appear in train | 4,261 / 6,120 (69.6%) | 4,250 / 6,246 (68.0%) |
| Distinct prompts that also appear in train | 3,694 / 5,525 (66.9%) | 3,711 / 5,666 (65.5%) |
| Distinct prompts found only in this split | 1,773 | 1,897 |

Validation and test also share 686 distinct prompts with each other. In practice, a model scored on test is mostly being scored on prompts it was trained on. Only about 1,900 test prompts are unseen.

To fix this, apply the rules above, remove duplicates, then re-split the 59,733 distinct prompts so no prompt appears in more than one split. Near-duplicate variants of the same prompt (like the "cute furry monster" family) will still cross splits unless they are grouped first. The script that does the classification is at `C:\Users\Sangnope\AppData\Local\Temp\claude\991ff9898a57a9d7\0ceeb81b-0ac2-47d1-844a-38d8e6a5bfd6\scratchpad\clean.py`, and I can turn it into a script that writes out a cleaned CSV.

## P2

**Request time:** 2026-11-11T06:20:54.062Z

**Prompt:**

> Excluding rows that are not real prompts and removing duplicates, describe what a typical prompt looks like: its length in words, how often Midjourney parameters such as --ar, --no, --w/--h, --stop and --seed are used, and the most common aspect ratios.

**Response:**

I'll take the 59,733 distinct real prompts from the previous step and measure their length, parameter use and aspect ratios.

---

Quick check: my flag pattern also accepted a single hyphen. That could falsely count text like "…-no" or "…-h", so I'll recount the key flags with proper dashes only.

---

A typical prompt is about **12–13 words** of comma-separated description: a subject followed by style and quality keywords. It has a 46% chance of carrying a Midjourney parameter, and when it sets a shape, that shape is most often **16:9**. All figures below are for the 59,733 distinct real prompts from the previous step.

## Length

| | Median | Mean | Middle half | 90th pct | Max |
|---|---:|---:|---:|---:|---:|
| Words, including parameters | 13 | 17.2 | 7–22 | 35 | 353 |
| Descriptive words, parameters removed | **12** | 15.7 | 7–20 | 33 | 353 |

| Descriptive words | Share of prompts |
|---|---:|
| 1–5 | 18.7% |
| 6–10 | 26.3% |
| **11–20** | **30.2%** |
| 21–30 | 13.2% |
| 31–50 | 9.2% |
| 51+ | 2.5% |

The mean is above the median because a small number of very long prompts pull it up. Prompts are mostly keyword lists rather than sentences: about half (48.7%) contain two or more commas. Two median-length examples:
- *"euclyptus leaves tattoo, forest, depth, foreground, background, blue tones, gustav klimpt style --ar 3:7"*
- *"bear::3 eating a pot of gold coins::1, beautiful illustration, fantasy, by yoshitaka amano, frazetta --ar 9:16"*

## Parameter usage

**46.2%** of prompts use at least one parameter.

| Parameter | Prompts | Share | Notes |
|---|---:|---:|---|
| `--ar` or `--aspect` | 21,102 | **35.3%** | `--ar` 30.7%, the long form `--aspect` 4.6% |
| `--w` / `--h` | 3,907 | 6.5% | Usually as a pair (3,052); top sizes 1920×1080, 1792×1024, 1080×720 |
| `--uplight` | 3,114 | 5.2% | Lighter upscaler (early Midjourney) |
| `--no` | 2,359 | 3.9% | Top exclusions: dof (643), blur (356), people (274), text (171) |
| `--stop` | 751 | 1.3% | Almost always 80 (427), then 85 and 90 |
| `--wallpaper`, `--test`, `--hd` | ~700 each | ~1.2% | Early-era options |
| `--iw` (image weight) | 205 | 0.3% | |
| `--seed` | 165 | 0.3% | Rare: few people tried to reproduce exact results |

- No prompt uses `--v`, `--q`, `--stylize`, `--chaos`, `--tile` or `--niji`. That fits the 2022 beta period, before those options were common.
- About 13% of parameters are written with an em dash (`—ar`) instead of `--`, which is what phones and autocorrect produce. I counted both forms.

## Aspect ratios

35.3% of prompts set a ratio with `--ar`/`--aspect` (21,080 with a readable value). Among those, as typed:

| Ratio | Share | | Ratio | Share |
|---|---:|---|---|---:|
| **16:9** | **33.0%** | | 11:17 | 2.6% |
| 9:16 | 12.1% | | 3:2 | 2.3% |
| 2:3 | 7.3% | | 2:1 | 2.1% |
| 4:5 | 3.9% | | 4:3 | 1.9% |
| 16:8 | 3.3% | | 7:5 | 1.8% |
| 3:4 | 2.9% | | 21:9 | 1.7% |

- Including `--w`/`--h` sizes and simplifying equivalent ratios (16:8 → 2:1) gives 24,130 prompts. The order barely changes: 16:9 31%, 9:16 11%, 2:3 8%, 2:1 5%.
- **Landscape leads: 54% landscape, 44% portrait, under 2% square.** Since square was Midjourney's default then, the people who changed the shape mostly wanted widescreen or phone-wallpaper formats.

How I counted:
- A parameter counts if it starts with `--`, `—` or `–`. I first allowed a single `-` too, but that changed the numbers by under 0.1 percentage points, so I dropped it.
- "Descriptive words" means whatever is left after removing flags, numbers, ratios, URLs and mentions.

The script is at `C:\Users\Sangnope\AppData\Local\Temp\claude\991ff9898a57a9d7\0ceeb81b-0ac2-47d1-844a-38d8e6a5bfd6\scratchpad\typical.py`.

## P3

**Request time:** 2026-11-11T06:22:16.940Z

**Prompt:**

> What share of prompts reference a named artist or "in the style of" someone? Which artists are named most often? What share use generic quality phrases such as "trending on artstation", "8k" or "octane render"? State the rule you used to detect each.

**Response:**

I'll start by pulling out the phrases that follow "by", "style of" and "inspired by". Those will show which names actually appear before I settle on detection rules.

---

The shell choked on the quoting in that long heredoc, so I'll write the script with the file tool instead.

---

The name list could have false matches: "mobius" could be a Möbius strip, "bosch" the brand, "hewlett" Hewlett-Packard, "mucha" the Spanish word. I'll audit the riskier aliases before reporting.

---

Only one alias needed fixing: "mobius" also matches "Möbius strip" (49 prompts). I'll exclude that and rerun.

---

**About 28% of prompts name an artist or use "in the style of"/"by" wording, and about 33% use at least one generic quality phrase.** The most-named artist is Craig Mullins, in 2.2% of prompts. All figures are for the 59,733 distinct real prompts from before.

## Artist and style references

| Measure | Prompts | Share |
|---|---:|---:|
| A. Uses style-attribution wording | 10,257 | 17.2% |
| B. Names an artist from my list | 12,747 | 21.3% |
| **A or B** | **16,450** | **27.5%** |
| Both A and B | 6,554 | 11.0% |
| A only (the name isn't on my list) | 3,703 | 6.2% |
| B only (a bare name, no "by" or "style of") | 6,193 | 10.4% |

A third (34%) of the prompts that name a listed artist name two or more, e.g. "james jean, mucha, beksinski".

**Rule A (wording):** a prompt counts if either of these is true:
- It contains "in the style of", "style of", "in the manner of", "inspired by", "styled after" or "in the vein of" (7.9%).
- It contains **"by" + a word**, where "by" comes right after an art word or punctuation. The art words are things like *art, artwork, painting, painted, drawn, illustration, photo, photography, design, render, poster, directed, cinematography, style*; the punctuation is a comma, colon, `+`, `|`, a bracket, or the start of the prompt (9.5%).

The art-word condition is there to exclude non-attribution uses like "surrounded by" or "covered by", which are common. This rule catches artists not on my list (e.g. "artwork by Józef Mehoffer", "by Noah Bradley"). It also catches some non-person references, like "in the style of rococo" or "in the style of Archie Comics". So it is a broad measure.

**Rule B (named artist):**
- I built a list of 168 individual people from the most frequent names that follow "by"/"style of" in this data. It covers painters, illustrators, photographers and filmmakers, plus common aliases and misspellings (e.g. *alfons/alphonse mucha*, *kindkade* → Kinkade, *beksinkski* → Beksiński).
- Each name matches anywhere as a whole word, case-insensitive, after removing `--` parameters.
- I audited the ambiguous names. "Mobius" also matched "Möbius strip" in 49 prompts, so I excluded that phrase. The other checked names (Dalí, Bosch, Mucha, Hewlett, Monet…) were genuine artist mentions in the samples I checked.
- Studios are excluded because they aren't individuals. If Studio Ghibli counted, it would rank #1 with 1,272 prompts (2.1%); Pixar has 400 and Disney 188.

Because it relies on a list, this is a lower bound: rare artists not on the list are missed.

## Most-named artists (share of all prompts)

| # | Artist | Prompts | Share | | # | Artist | Prompts | Share |
|---|---|---:|---:|---|---|---|---:|---:|
| 1 | Craig Mullins | 1,287 | 2.15% | | 11 | Zdzisław Beksiński | 397 | 0.66% |
| 2 | Peter Mohrbacher | 966 | 1.62% | | 12 | Ross Tran | 386 | 0.65% |
| 3 | Alphonse Mucha | 814 | 1.36% | | 13 | Mike Mignola | 382 | 0.64% |
| 4 | Hayao Miyazaki | 704 | 1.18% | | 14 | Marc Simonetti | 345 | 0.58% |
| 5 | H. R. Giger | 675 | 1.13% | | 15 | Ansel Adams | 332 | 0.56% |
| 6 | Moebius (Jean Giraud) | 606 | 1.01% | | 16 | Brian Froud | 331 | 0.55% |
| 7 | James Jean | 516 | 0.86% | | 17 | Greg Rutkowski | 306 | 0.51% |
| 8 | Artgerm | 513 | 0.86% | | 18 | WLOP | 306 | 0.51% |
| 9 | James Gurney | 423 | 0.71% | | 19 | Claude Monet | 304 | 0.51% |
| 10 | Ashley Wood | 401 | 0.67% | | 20 | Hokusai | 287 | 0.48% |

- The list is led by living concept artists and illustrators (Mullins, Mohrbacher, James Jean, Artgerm, Ross Tran, WLOP), with a few classic names mixed in (Mucha, Monet, Hokusai).
- Greg Rutkowski, later the best-known "AI-prompted artist", is only #17 here. That fits this data coming from early Midjourney (2022).
- These counts are of distinct prompts. Users often submitted many small variants of one prompt, so a few heavy users can push a name up. Craig Mullins and Brian Froud, for example, appear in long lists that were re-run many times.

## Generic quality phrases

**33.1% of prompts (19,783) contain at least one quality booster, and 18.2% contain at least one of "trending on artstation", "8k" or "octane render".**

| Phrase | Rule (whole word, case-insensitive) | Share |
|---|---|---:|
| Hyper-/photo-/ultra-realistic | `hyper`/`ultra`/`super`/`photo` + `realistic`/`realism`, with or without a space or hyphen | 13.6% |
| Octane render | the word `octane` | 10.0% |
| 8k | `8k` or `8 k` | 9.9% |
| Highly/hyper/ultra detailed | `highly`/`hyper`/`ultra`/`super`/`extremely`/`very`/`insanely` + `detail(ed)` | 9.6% |
| 4k | `4k` or `4 k` | 5.3% |
| Unreal Engine | the word `unreal` | 4.8% |
| Trending on ArtStation | `trending on artstation` or `trending on art station` | 3.8% |
| Volumetric lighting | `volumetric` | 2.0% |
| High resolution / quality | `high res`, `high resolution`, `high quality` or `high definition` | 2.0% |
| Renderer names | `vray`, `redshift`, `blender`, `c4d`, `cinema 4d` or `houdini` | 1.9% |
| CGSociety | `cgsociety` | 1.8% |
| HDR / UHD | `hdr` or `uhd` | 0.5% |
| Ray tracing | `ray tracing` (also `raytracing`) | 0.4% |
| Masterpiece, award winning, sharp focus | the phrase itself | ≤0.1% each |

- **"Any quality booster" means any phrase in the table above.** I deliberately left out words that also describe content or mood: "cinematic" (10.4%), plain "realistic" (12.4%), "artstation" without "trending" (8.7% total), "intricate" (5.0%), "beautiful" (5.8%) and "epic" (4.1%). Counting those would raise the total.
- **Boosters stack.** Of the prompts that use any, about half use two or more, and some use 6–10.
- **Boosters go with artist names.** 47% of artist-naming prompts also use a booster, compared with 29% of other prompts.
- "Masterpiece", "sharp focus" and "award winning", which later became stock phrases, barely appear (under 0.2%). That also fits a 2022 snapshot.

The script, including the full artist list, is at `C:\Users\Sangnope\AppData\Local\Temp\claude\991ff9898a57a9d7\0ceeb81b-0ac2-47d1-844a-38d8e6a5bfd6\scratchpad\artists.py`.

## P4

**Request time:** 2026-11-11T06:27:40.511Z

**Prompt:**

> Identify the main themes or topics in the prompts using a topic model. Report the topics with their top words and the share of prompts in each. How stable are these topics if the analysis is re-run?

**Response:**

I'll check which libraries are available for topic modelling, since the Python install is partly broken.

---

Before running, I'll stop common English words that also happen to be artist surnames ("wood", "grey", "bacon", "hopper"…) from being stripped, since they can be real subject words.

---

Small slicing bug in how I pull in the artist list; I'll split on the code line rather than the comment.

---

That sed edit was messy. I'll replace lines 32–34 with a clean version using the file tool.

---

I ran topic models over the ~56,000 distinct prompts. **The themes are recognisable, but the results are only moderately stable. Treat the topic list as a rough map, not as reliable percentages.**

## How I ran it
- **Data:** the 59,733 distinct real prompts. I removed parameters, URLs and weights, and merged prompts that became identical, leaving 56,265.
- **Model:** NMF on word and two-word-phrase frequencies (TF-IDF), with common English words removed. Each prompt is assigned to its strongest topic.
- **Two versions:**
  - **Model A** used all words. Its topics turned out to be mostly style boilerplate: "octane render", "unreal engine", "highly detailed cgsociety", "trending on artstation", "cinematic lighting", "hyper realistic". That matches the earlier finding that a third of prompts use these phrases.
  - **Model B** removed about 150 style and quality words plus artist names. It shows subject matter, so it is the main result below.
- **Number of topics:** I tested 6–28 per model. Coherence (whether a topic's top words tend to appear together) fell as topics were added, and stability peaked at 16–18. I report 16 for Model B; a 10-topic version gave the same main themes.

## Subject themes (Model B, 16 topics)

| Theme (my label) | Top words | Share | Share across 20 seeds | Stability* |
|---|---|---:|---:|---:|
| Landscapes, nature, sky (catch-all) | forest, sky, landscape, night, world, red, blue, green, clouds, tree | **31.4%** | 6–41% | 0.63 |
| Characters: girls/women, faces, anime | girl, face, character, woman, hair, cute, eyes, anime, wearing | 11.3% | 8–18% | 0.91 |
| Black & white, ink, logos | black, white, black white, red, logo, ink, black ink, film, paper | 9.3% | 4–11% | 0.81 |
| Cyberpunk & post-apocalyptic cities | city, cyberpunk, futuristic, apocalyptic, night, neon, street, future | 6.1% | 4–11% | 0.65 |
| Space & spaceships | space, deep space, ship, station, space station, nebula, interior | 6.0% | 4–12% | 0.88 |
| Dark fantasy & horror | dark, dark fantasy, fantasy, horror, dark forest, vintage, medieval | 4.8% | 3–28% | 0.49 |
| Ornate "golden ratio" style | james jean, golden, ornate, luxury, hypermaximalist, golden ratio | 4.6% | 4–11% | 0.68 |
| Old men, grotesque, everyday scenes | man, old man, grotty, head, real, playing, computer, room | 4.4% | 4–6% | 0.86 |
| Painted character portraits | portrait, character portrait, female, oil, bowater, edmund leighton | 3.7% | 3–6% | 0.92 |
| Tarot cards, ink & fractals | card, tarot card, paper, black paper, ink, fractal, line, gold | 3.4% | 2–13% | 0.39 |
| Alien sci-fi, blue & yellow | sci fi, alien, blue, yellow, patterns, pharaonic | 3.1% | 2–5% | 0.91 |
| Psychedelic, vibrant animals | psychedelic, cat, vibrant, macro, waves, dragon, sunset, rabbit | 2.7% | 2–5% | 0.91 |
| Pulp fantasy magazine | fantasy, pulp, magazine circa, thrasher, chromatic | 2.5% | 2–3% | 1.00 |
| Body-building / muscles | building, body, extreme muscles, body builder, mechanical | 2.4% | 2–4% | 0.88 |
| Clay figures (Mario, Koopa) | clay, cute, koopa, clay animation, dinosaur, sculpture | 1.1% | 1–2% | 1.00 |
| Danny DeVito | danny devito, screen capture, dune, gnome | 0.5% | 0.5–8% | 0.84 |
| No topic words left after filtering | — | 2.7% | — | — |

\*Stability = average share of the topic's top 10 words that reappear in the best-matching topic across 20 re-runs with different random seeds (1.00 = identical every time).

**What the themes say:**
- The broad subject areas are scenery, characters and portraits, sci-fi (cities, space, aliens), and dark fantasy/horror.
- Several small topics are **one user's prompt template re-run many times with small changes**, not broad themes. Examples: "…pulp art fantasy magazine circa", "…made of clay" (Mario characters), "…extreme muscles", "…blue and yellow pharaonic patterns", and Danny DeVito.
- These template topics are the *most* stable precisely because they repeat word-for-word. High stability here does not mean the topic is important.
- Two artist names slipped through the filter ("James Jean", "Bowater/Edmund Leighton"). I had kept a few surname words that are also ordinary words so they wouldn't be stripped as subjects, and these names were among them. Those two topics are partly artist templates too.

## How stable is it if re-run?

| Change on re-run | Model A (style) | Model B (subject) |
|---|---:|---:|
| Different random seed: top-word overlap | 0.84 | 0.80 |
| Random 80% of the data: top-word overlap | 0.75 | 0.73 |
| Different seed: prompt lands in the same topic | 77% (worst 70%) | 75% (worst 56%) |
| Different method (LDA) vs NMF: top-word overlap | 0.17 | 0.23 |
| LDA re-run vs itself | 0.27 | 0.22 |

- **Topic word lists are fairly reproducible with the same method.** Most topics come back with 7–9 of the same top 10 words.
- **Assignments and shares are not.** A quarter of prompts switch topic between runs. The catch-all landscape topic ranges from 6% to 41% depending on the seed, and dark fantasy from 3% to 28%. The percentages above come from one representative run (the one most similar to all others), so treat them as rough.
- **Results depend on the number of topics.** Some themes persist from 12 to 24 topics (space, clay, pulp fantasy, sci-fi aliens). Others split or merge (dark fantasy, tarot, the catch-all).
- **They also depend on the method.** LDA, a different standard topic model, finds largely different topics, and isn't even consistent with itself. Prompts are short keyword lists (median 12 words), which is a hard setting for these models.

**Conclusion:** the content is dominated by style boilerplate. Once that is removed, there are about 5–6 dependable subject themes plus many niche templates. The exact percentages can move by tens of points between runs. Classifying prompts into a few predefined categories with keyword rules would give more dependable shares than these topic shares.

The scripts are in `C:\Users\Sangnope\AppData\Local\Temp\claude\991ff9898a57a9d7\0ceeb81b-0ac2-47d1-844a-38d8e6a5bfd6\scratchpad\`: `tm_prep.py`, `tm_select.py` and `tm_final.py`. Set `TM_MODE=subject` and `TM_K=16` to reproduce Model B.

## P5

**Request time:** 2026-11-11T06:50:56.718Z

**Prompt:**

> Test two hypotheses and report the test, test statistic, p-value and an effect size for each: (H1) prompts that use at least one parameter are longer than prompts that use none; (H2) prompts that name an artist are more likely to use a quality phrase.

**Response:**

I'll test both hypotheses on the 59,733 distinct prompts, reusing the definitions from earlier:
- "Uses a parameter": has a `--`/`—`/`–` flag.
- "Length": descriptive words with parameters removed, so the flags themselves don't make the answer automatic.
- "Names an artist": the 168-name list.
- "Quality phrase": the core booster set.

I'll also check whether the results hold up to duplicates and to prompt length.

---

No statsmodels, so I'll use scipy and write the logistic regression myself (a few lines of numpy).

---

The slice I took from the artist script dropped its `import random` line; I'll add the import.

---

**Both hypotheses are supported as stated, but only H1 holds up on closer inspection.**
- **H1:** prompts with parameters are clearly longer, by a medium-to-large margin.
- **H2:** artist-naming prompts do use quality phrases more often, but this is almost entirely because they are longer. Once length is accounted for, the association disappears.

All tests use the 59,733 distinct real prompts and the definitions from earlier.

## H1: prompts with a parameter are longer

**Definitions:**
- **Parameter:** any `--`, `—` or `–` flag. 27,586 prompts have one; 32,147 have none.
- **Length:** descriptive words, with the parameters and their values removed. Otherwise the flags would make the parameter prompts longer automatically.

**Test:** one-sided Mann-Whitney U. Lengths are heavily skewed, so I compared ranks rather than means.

| | With parameter | Without |
|---|---:|---:|
| Median words | **16** | **9** |
| Mean words | 20.2 | 11.9 |

| Result | Value |
|---|---|
| Test statistic | U = 6.25 × 10⁸, z = 86.3 |
| p-value (one-sided) | ≈ 10⁻¹⁶²¹, effectively 0 |
| **Effect size** | **Rank-biserial r = 0.41.** A random parameter prompt is longer than a random no-parameter prompt 70% of the time. |
| Other effect measures | Median difference 7 words (bootstrap 95% CI 7 to 7); typical shift (Hodges-Lehmann) 6 words; Cohen's d = 0.62 |
| Check: Welch t-test on means | t = 73.8, p ≈ 0 |
| Check: near-duplicates collapsed (56,284 prompts) | r = 0.41, medians 16 vs 9: unchanged |

**Verdict: supported, with a medium-to-large effect.** This shows the two go together, not that one causes the other. The likely explanation is that more engaged users both write more and adjust settings.

## H2: artist-naming prompts more often use a quality phrase

**Definitions:**
- **Artist:** names someone on the 168-name list (12,747 prompts).
- **Quality phrase:** any of the core boosters ("8k", "octane render", "trending on artstation", etc.; 19,783 prompts).

**Test:** chi-square test of independence on the 2×2 table, plus a one-sided Fisher exact test.

| | Quality phrase | None | Rate |
|---|---:|---:|---:|
| Names an artist | 6,033 | 6,714 | **47.3%** |
| No artist | 13,750 | 33,236 | **29.3%** |

| Result | Value |
|---|---|
| Test statistic | χ²(1) = 1,477 (one-sided z = 38.4) |
| p-value | ≈ 10⁻³²² (Fisher one-sided ≈ 10⁻³¹¹) |
| **Effect size** | **Odds ratio 2.17 (95% CI 2.09–2.26)** |
| Other effect measures | Risk ratio 1.62; risk difference +18.1 points (17.1–19.0); φ = 0.16, a small association |
| Check: near-duplicates collapsed | OR 2.19, φ = 0.16: unchanged |

**This association is mostly explained by prompt length.** Artist prompts are much longer, and longer prompts are much more likely to contain any given phrase. When I held length constant (counting words other than the artist's name, since the name itself adds about 2.3 words), the association disappears:

| Length-controlled analysis | Odds ratio for artist |
|---|---|
| Logistic regression: quality ~ artist + log(length) | **0.95 (0.91–1.00)**, z = −2.1, p = 0.04 |
| Mantel-Haenszel, across 7 length bands | **1.01** |

Within length bands, the direction depends on length:

| Non-artist words | Quality rate: artist vs none | Odds ratio |
|---|---|---:|
| 1–5 | 2.9% vs 4.3% | 0.67 |
| 6–20 | about 3–5 points lower for artist prompts | 0.78–0.83 |
| 21–30 | 62.4% vs 61.7% | 1.03 |
| 31–50 | 77.6% vs 68.4% | 1.60 |
| 51+ | 89.3% vs 64.5% | 4.62 |

The change across length bands is itself significant (interaction OR 1.34 per log-unit of length, p ≈ 2 × 10⁻¹⁰).

**Verdict: supported as stated, but not as a direct link.** In short and medium prompts, naming an artist goes with slightly *fewer* quality boosters; people seem to use one or the other. Only very long "kitchen-sink" prompts pile up both. The overall odds ratio of 2.17 comes mainly from length, so I wouldn't report it alone.

**Caveat for both:** p-values assume prompts are independent. They aren't fully independent, because many prompts are variants from the same user or template. With about 60,000 prompts, almost any difference is "significant", so the effect sizes are the meaningful numbers.

The scripts are `hypo.py` and `hypo2.py` in `C:\Users\Sangnope\AppData\Local\Temp\claude\991ff9898a57a9d7\0ceeb81b-0ac2-47d1-844a-38d8e6a5bfd6\scratchpad\`.

## P6

**Request time:** 2026-11-11T06:57:00.634Z

**Prompt:**

> Give me the complete code you ran for all of the above, in one block, so that I can reproduce your results.

**Response:**

I'll combine the scripts into one file, run it from scratch, and check that it reproduces the numbers I reported. First I'll read the current versions of every script, since several were patched with sed along the way.

---

I have the current version of every script. I'll combine them into one file with a section for each question, run it end to end, and check its output against the numbers I reported.

---

The full run, including the topic models, is going in the background and takes several minutes. When it finishes, I'll check its output against the reported figures.

---

I don't need the monitor: the background run will notify me when it finishes. Once it does, I'll check its output against the numbers I reported, then give you the single code block.

---

The run finished without errors. I'll check the key numbers against what I reported.

---

The rerun is still going (the topic models are the slow part). It will notify me when it's done, and then I'll confirm the numbers match.

---

Everything now matches the numbers I reported, including every topic share and stability figure. I'll print the final file so the block below is exactly what ran.

---

The combined script below reproduces all six analyses and matches every number I reported. I ran it end to end, fixed two small differences from the original scripts, then reran the affected sections to confirm the match.

Run it with:

```
PYTHONIOENCODING=utf-8 python -I reproduce_all.py midjourney_prompts_all.csv          # everything
PYTHONIOENCODING=utf-8 python -I reproduce_all.py midjourney_prompts_all.csv q2 q6    # chosen sections
```

- **Runtime:** sections q1–q4 and q6 take about a minute together. q5 (topic models) takes 10+ minutes.
- **Libraries:** numpy, scipy and scikit-learn only; pandas isn't used. I ran it with Python 3.15.0, numpy 2.5.4, scipy 1.18.1 and scikit-learn 1.9.1.
- **Topic-model results** depend on exact library versions, because the random starting points can differ between versions. On other versions, expect similar topics and stability figures, not identical decimals.
- **Section q1** is my first exploratory pass. Its rough "4+ words" cut was replaced by the rules in q2.
- **Not included:** the scripts that hit errors and were rerun.

The file is also saved at `C:\Users\Sangnope\AppData\Local\Temp\claude\991ff9898a57a9d7\0ceeb81b-0ac2-47d1-844a-38d8e6a5bfd6\scratchpad\reproduce_all.py`.

```python
"""
Reproduce every analysis of midjourney_prompts_all.csv from this session.

Usage:
    python -I reproduce_all.py midjourney_prompts_all.csv            # all sections
    python -I reproduce_all.py midjourney_prompts_all.csv q2 q6      # selected sections

Sections:
    q1  first overview (exploratory; its rough "4+ words" cut was later replaced by the q2 rules)
    q2  data cleanliness: row classes, duplicates, split overlap
    q3  typical prompt: length, parameters, aspect ratios
    q4  artist references and quality phrases
    q5  topic models (Model A: all words, K=18; Model B: style words removed, K=10 and K=16) + stability
    q6  hypothesis tests H1 and H2

Run with: Python 3.15.0, numpy 2.5.4, scipy 1.18.1, scikit-learn 1.9.1 (standard library otherwise; pandas not used).
q5 takes several minutes. Set PYTHONIOENCODING=utf-8 on Windows so non-ASCII names print.
"""
import csv, re, sys, os, io, random, itertools, statistics as st, warnings
from collections import Counter
from math import gcd
warnings.filterwarnings('ignore')

CSV = sys.argv[1]
SECTIONS = sys.argv[2:] or ['q1', 'q2', 'q3', 'q4', 'q5', 'q6']

# =====================================================================================
# Common: load rows, classify each row, list of distinct real prompts P
# =====================================================================================
rows = list(csv.DictReader(open(CSV, encoding='utf-8', newline='')))
N = len(rows)
PARAM = re.compile(r'^(?:--?|—|–)[A-Za-z]+$')                                       # --ar, —ar, --uplight
VAL = re.compile(r'^(?:\d+(?:\.\d+)?(?:\s*[:x/]\s*\d+(?:\.\d+)?)?|::-?\d*\.?\d*)$')   # 16:9, 1920, 0.5, ::0.75
URL = re.compile(r'^<?https?://\S+>?$')
MENTION = re.compile(r'^@\S+$|^<@!?\d+>$')

def leftover(t):
    """Tokens left after removing parameter flags, numbers/ratios/weights, URLs, mentions and /imagine."""
    return [w for w in t.split() if not (PARAM.match(w) or VAL.match(w) or URL.match(w) or MENTION.match(w)
                                         or w.lower() in ('/imagine', 'imagine'))]

def words(ws):
    """Keep tokens that contain at least one letter."""
    return [w for w in ws if re.search(r'[A-Za-z\u00c0-\uffff]', w)]

def classify(t):
    if not t.strip(): return 'A empty'
    toks = t.split()
    if all(URL.match(w) for w in toks): return 'B url only'
    if all(MENTION.match(w) for w in toks): return 'C user mention only'
    rest = leftover(t)
    if not words(rest): return 'D parameters/numbers only'
    if len(words(rest)) == 1 and len(toks) == 1: return 'E fragment (lone word)'
    if len(words(rest)) == 1: return 'F1 one word + params'
    if len(words(rest)) == 2: return 'F2 two words'
    return 'F prompt'

cls = [classify(r['text']) for r in rows]
P = list(dict.fromkeys(r['text'] for r, c in zip(rows, cls) if c.startswith('F')))   # 59,733 distinct real prompts


# =====================================================================================
# q1: first overview (exploratory)
# =====================================================================================
def q1():
    print('\n' + '=' * 30, 'q1 first overview (exploratory)', '=' * 30)
    print("rows", len(rows), Counter(r['split'] for r in rows))
    T = [r['text'] for r in rows]
    print("empty", sum(1 for t in T if not t.strip()))
    c = Counter(T); print("unique", len(c), "dup rows", len(T) - len(c))
    wc = [len(t.split()) for t in T]; s = sorted(wc)
    q = lambda p: s[int(p * (len(s) - 1))]
    print("words mean", st.mean(wc), "pcts", [(p, q(p)) for p in (.1, .25, .5, .75, .9, .99)], "max", s[-1])
    for k in (1, 2, 3, 5): print(f"<= {k} words", sum(w <= k for w in wc) / len(wc))
    print("chars max", max(len(t) for t in T))
    print(c.most_common(40))
    f = lambda pat: sum(1 for t in T if re.search(pat, t)) / len(T)
    print("ratio only", sum(1 for t in T if re.fullmatch(r'\s*[\d.]+\s*[:x]\s*[\d.]+\s*', t)) / len(T))
    print("url any", f(r'https?://'), "url only", sum(1 for t in T if re.fullmatch(r'\s*<?https?://\S+>?\s*', t)) / len(T))
    print("has --param", f(r'--\s?[a-z]'), "em-dash param", f(r'—[a-z]'), "starts /", f(r'^/'))
    print("numeric only", sum(1 for t in T if re.fullmatch(r'\s*[\d.,]+\s*', t)) / len(T))
    sp = {}
    for r in rows: sp.setdefault(r['split'], set()).add(r['text'])
    ks = list(sp)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)): print(ks[i], ks[j], "overlap", len(sp[ks[i]] & sp[ks[j]]))

    tr = set(r['text'] for r in rows if r['split'] == 'train')
    for spl in ('test', 'validation'):
        R = [r['text'] for r in rows if r['split'] == spl]
        print(spl, "rows in train", sum(t in tr for t in R) / len(R), "full(>=4w) rows in train",
              sum(t in tr for t in R if len(t.split()) >= 4) / sum(1 for t in R if len(t.split()) >= 4))
    full = [t for t in T if len(t.split()) >= 4]
    U = list(dict.fromkeys(full))
    print("full rows", len(full), "unique full", len(U))
    cf = Counter(full); print("top repeated full prompts"); [print(n, repr(t[:110])) for t, n in cf.most_common(12)]
    print("unique full prompts appearing once", sum(1 for v in cf.values() if v == 1) / len(cf))
    def norm(t):
        t = re.sub(r'(--|—)\s?\w+(\s+[\w:.]+)?', '', t.lower()); return re.sub(r'[^a-z0-9 ]', '', ' '.join(t.split()))
    print("unique after normalising params/punct", len(Counter(norm(t) for t in U)))
    wcu = sorted(len(t.split()) for t in U); print("full unique words median", wcu[len(wcu) // 2], "p90", wcu[int(.9 * len(wcu))])
    Pm = Counter(); AR = Counter(); V = Counter()
    for t in U:
        t2 = t.replace('—', '--')
        for m in re.finditer(r'--\s?([a-zA-Z]+)', t2): Pm[m.group(1).lower()] += 1
        m = re.search(r'--(?:ar|aspect)\s+(\d+\s*:\s*\d+)', t2)
        if m: AR[m.group(1).replace(' ', '')] += 1
        m = re.search(r'--v(?:ersion)?\s+(\d)', t2)
        if m: V[m.group(1)] += 1
    n = len(U)
    print("share with any param", sum(1 for t in U if re.search(r'(--|—)\s?[a-zA-Z]', t)) / n)
    print("params", [(k, v, round(v / n, 3)) for k, v in Pm.most_common(25)])
    print("AR", AR.most_common(12), "total", sum(AR.values()))
    print("versions", V)
    print("emdash", sum('—' in t for t in U) / n)
    kw = ['highly detailed', 'detailed', '8k', '4k', 'octane render', 'unreal engine', 'artstation', 'trending on artstation', 'cinematic',
          'photorealistic', 'hyper realistic', 'hyperrealistic', 'realistic', 'volumetric lighting', 'concept art', 'digital art', 'portrait',
          'by greg rutkowski', 'greg rutkowski', 'studio ghibli', 'beautiful', 'epic', 'intricate', 'sharp focus', 'dramatic lighting', 'fantasy',
          'cyberpunk', 'steampunk', 'anime', 'oil painting', 'watercolor', 'photograph', '35mm', 'bokeh', 'depth of field', 'art nouveau',
          'surreal', 'dark', 'moody', 'hdr', 'ray tracing', 'cgsociety', 'vray', 'blender', 'pixar', 'disney', 'sci-fi', 'dystopian',
          'post apocalyptic', 'gothic', 'horror', 'lovecraft', 'minimalist', 'vaporwave', 'synthwave', 'isometric', 'low poly', 'pixel art',
          'logo', 'wallpaper']
    Lw = [t.lower() for t in U]
    print("keywords"); print(sorted([(k, round(sum(k in t for t in Lw) / n, 4)) for k in kw], key=lambda x: -x[1]))
    names = ['craig mullins', 'peter mohrbacher', 'miyazaki', 'giger', 'monet', 'studio ghibli', 'james jean', 'artgerm', 'moebius',
             'james gurney', 'ross tran', 'alphonse mucha', 'marc simonetti', 'rutkowski', 'greg rutkowski', 'wlop', 'hokusai', 'hr giger',
             'beksinski', 'wes anderson', 'norman rockwell', 'klimt', 'tom bagshaw', 'makoto shinkai', 'yoshitaka amano', 'rembrandt',
             'escher', 'loish', 'thomas kinkade', 'picasso', 'hayao miyazaki', 'van gogh', 'mobius', 'tim burton', 'beeple']
    print("names", sorted([(k, sum(k in t for t in Lw)) for k in names], key=lambda x: -x[1]))
    Uall = set(t.lower() for t in T if len(t.split()) >= 4)
    print("content mentions", [(k, sum(k in t for t in Uall)) for k in
          ['nude', 'naked', 'sexy', 'blood', 'gore', 'trump', 'biden', 'putin', 'batman', 'darth vader', 'star wars']])
    print("cjk/cyrillic unique", sum(1 for t in set(T) if re.search(r'[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af\u0400-\u04ff]', t)))
    short = Counter(t for t in T if len(t.split()) == 1 and t.strip())
    blob = ' '.join(set(t.lower() for t in T if len(t.split()) >= 4))
    top = [w for w, _ in short.most_common(300)]
    print("share of top-300 single-token rows found inside full prompts", sum(w.lower() in blob for w in top) / 300)


# =====================================================================================
# q2: cleanliness
# =====================================================================================
def q2():
    print('\n' + '=' * 30, 'q2 cleanliness', '=' * 30)
    C = Counter(cls)
    print("ALL", N)
    for k in sorted(C): print(f"{k:28s}{C[k]:8d}{C[k]/N:8.1%}")
    for k in sorted(C):
        ex = [r['text'] for r, c in zip(rows, cls) if c == k]
        print(k, 'eg:', [e[:50] for e in Counter(ex).most_common(8)])
    # evidence that lone words are fragments: do they occur inside prompts of 4+ words?
    nw = lambda t: len(words(leftover(t)))
    big = '\n'.join(set(r['text'].lower() for r in rows if nw(r['text']) >= 4))
    for k in (1, 2, 3):
        d = sorted(set(r['text'] for r, c in zip(rows, cls) if nw(r['text']) == k and c[0] in 'EF'))
        print(f"{k}-word distinct texts {len(d)}: found inside a 4+ word prompt {sum(t.lower().strip() in big for t in d)/len(d):.1%}")
    lone = [r['text'] for r, c in zip(rows, cls) if c.startswith('E')]
    big_raw = '\n'.join(set(r['text'].lower() for r in rows if len(r['text'].split()) >= 4))   # prompts with 4+ raw tokens
    cl = Counter(lone); out = {t: n for t, n in cl.items() if t.lower() not in big_raw}
    print(len(lone), "lone-word rows;", sum(out.values()), "rows /", len(out), "distinct NOT inside a 4+ word prompt")
    # duplicates
    cnt = Counter(r['text'] for r in rows); print("distinct texts", len(cnt), "exact dup rows (beyond 1st)", N - len(cnt))
    Pr = [r['text'] for r, c in zip(rows, cls) if c.startswith('F')]
    pc = Counter(Pr); print("prompt rows", len(Pr), "distinct prompts", len(pc), "dup prompt rows", len(Pr) - len(pc))
    norm = lambda t: ' '.join(t.lower().split())
    print("distinct prompts after case/whitespace normalisation", len(set(map(norm, pc))))
    nonp = [r['text'] for r, c in zip(rows, cls) if not c.startswith('F')]; print("non-prompt rows", len(nonp), "distinct", len(set(nonp)))
    # split overlap
    by = {}
    for r, c in zip(rows, cls): by.setdefault(r['split'], []).append((r['text'], c))
    tr = set(t for t, _ in by['train']); trP = set(t for t, c in by['train'] if c.startswith('F')); trN = set(map(norm, trP))
    for spl in ('validation', 'test'):
        R = by[spl]; Ps = [t for t, c in R if c.startswith('F')]; Ds = set(Ps)
        print(spl, "rows", len(R), "| any row text in train", sum(t in tr for t, _ in R),
              "| prompt rows", len(Ps), "in train", sum(t in trP for t in Ps),
              "| distinct prompts", len(Ds), "in train", sum(t in trP for t in Ds), "norm", sum(norm(t) in trN for t in Ds))
    v = set(t for t, c in by['validation'] if c.startswith('F')); te = set(t for t, c in by['test'] if c.startswith('F'))
    print("distinct prompts shared val&test", len(v & te))
    print("distinct prompts unique to one split only: test", len(te - trP - v), "val", len(v - trP - te))


# =====================================================================================
# q3: typical prompt
# =====================================================================================
def q3():
    print('\n' + '=' * 30, 'q3 typical prompt', '=' * 30)
    n = len(P); print("distinct prompts", n)
    def q(v, ps=(.1, .25, .5, .75, .9, .99)):
        v = sorted(v); return [(p, v[int(p * (len(v) - 1))]) for p in ps]
    tot = [len(t.split()) for t in P]; desc = [len(words(leftover(t))) for t in P]
    print("total tokens mean", round(st.mean(tot), 1), q(tot), "max", max(tot))
    print("descriptive words mean", round(st.mean(desc), 1), q(desc), "max", max(desc))
    bins = [(1, 5), (6, 10), (11, 20), (21, 30), (31, 50), (51, 10**6)]
    print("desc bins", [(a, b, round(sum(a <= d <= b for d in desc) / n * 100, 1)) for a, b in bins])
    print("share with >=2 commas", round(sum(t.count(',') >= 2 for t in P) / n * 100, 1), "median commas", sorted(t.count(',') for t in P)[n // 2])
    D = r'(?:--|—|–)'
    def has(flag): return sum(1 for t in P if re.search(D + r'\s?' + flag + r'(?![a-z])', t, re.I))
    for f in ['ar', 'aspect', 'ar|aspect', 'no', 'w', 'h', 'w|h', 'stop', 'seed', 'sameseed', 'iw', 'hd', 'uplight', 'wallpaper', 'test',
              'testp', 'fast', 'vibe', 'video', 'q|quality', 's|stylize', 'v|version', 'chaos', 'tile', 'niji']:
        k = has('(?:' + f + ')'); print(f"--{f:12s}{k:7d}{k/n:7.1%}")
    anyp = sum(1 for t in P if re.search(r'(?:^|\s)(?:--|—|–)\s?[A-Za-z]', t)); print("any --param", anyp, anyp / n)
    print("w and h together", sum(1 for t in P if re.search(D + r'\s?w(?![a-z])', t, re.I) and re.search(D + r'\s?h(?![a-z])', t, re.I)))
    dash = Counter(m.group(1) for t in P for m in re.finditer(r'(--|—|–)\s?[A-Za-z]', t)); print("dash styles", dash)
    AR = Counter(); red = Counter(); orient = Counter()
    for t in P:
        m = re.search(D + r'\s?(?:ar|aspect)\s*(\d+(?:\.\d+)?)\s*[:x]\s*(\d+(?:\.\d+)?)', t, re.I); src = None
        if m: a, b = m.group(1), m.group(2); src = 'ar'
        else:
            w = re.search(D + r'\s?w\s*(\d+)', t, re.I); h = re.search(D + r'\s?h\s*(\d+)', t, re.I)
            if w and h: a, b = w.group(1), h.group(1); src = 'wh'
        if not src: continue
        try: fa, fb = float(a), float(b)
        except ValueError: continue
        if fa == 0 or fb == 0: continue
        if src == 'ar': AR[f"{a}:{b}"] += 1
        if fa.is_integer() and fb.is_integer():
            g = gcd(int(fa), int(fb)); red[f"{int(fa)//g}:{int(fb)//g}"] += 1
        orient['landscape' if fa > fb else 'portrait' if fa < fb else 'square'] += 1
    k = sum(AR.values()); print("prompts with --ar/--aspect ratio", k, k / n)
    print("as typed", [(r, c, round(c / k * 100, 1)) for r, c in AR.most_common(15)])
    K = sum(red.values()); print("reduced incl w/h", K, [(r, c, round(c / K * 100, 1)) for r, c in red.most_common(12)])
    O = sum(orient.values()); print("orientation", [(o, c, round(c / O * 100, 1)) for o, c in orient.items()])
    WH = Counter()
    for t in P:
        w = re.search(D + r'\s?w\s*(\d+)', t, re.I); h = re.search(D + r'\s?h\s*(\d+)', t, re.I)
        if w and h: WH[w.group(1) + 'x' + h.group(1)] += 1
    print("w x h", WH.most_common(8))
    NO = Counter(m.group(1).lower().strip() for t in P for m in re.finditer(D + r'\s?no\s+([A-Za-z][\w\- ]*?)(?=\s*(?:--|—|–|,|$))', t, re.I))
    print("--no values", NO.most_common(15))
    print("--stop values", Counter(m.group(1) for t in P for m in re.finditer(D + r'\s?stop\s*(\d+)', t, re.I)).most_common(8))
    random.seed(3); med = [t for t, d in zip(P, desc) if 12 <= d <= 16]
    print("median-length samples"); [print(' -', x[:200]) for x in random.sample(med, 6)]


# =====================================================================================
# q4: artists and quality phrases  (also defines things reused by q5 and q6)
# =====================================================================================
def strip_params(t):  # drop Midjourney flags and their value
    return re.sub(r'(?:--|—|–)\s?[a-zA-Z]+(?:\s+[\w:.]+)?', '', t.lower())

L = [strip_params(t) for t in P]

ARTW = (r"(?:art|artwork|arts|painting|paintings|painted|paint|drawing|drawn|drawings|illustration|illustrated|sketch|"
        r"photo|photograph|photography|photographed|photos|picture|image|design|designed|render|rendered|rendering|"
        r"sculpture|sculpted|poster|print|comic|cover|portrait|concept|directed|cinematography|filmed|shot|film|movie|"
        r"animation|animated|created|style|styled|work|works|engraving|etching|woodcut|lithograph|mural|watercolor|matte)")
R_STYLE = re.compile(r"\b(?:in the style of|style of|in the manner of|inspired by|styled after|in the vein of)\b")
R_BY = re.compile(r"(?:^|[,;:+|(\[]|\b" + ARTW + r"\b)\s*by\s+[a-z\u00c0-\u024f]")

# Curated list of individual artists: canonical name -> alias regexes (built from the most frequent names after by/style of)
A = {
 'Craig Mullins': [r'craig mullins?'], 'Peter Mohrbacher': [r'mohrbacher'], 'Hayao Miyazaki': [r'miyazaki'], 'H. R. Giger': [r'giger'],
 'Claude Monet': [r'monet'], 'James Jean': [r'james jean'], 'Artgerm': [r'artgerm'],
 'Moebius (Jean Giraud)': [r'(?:moebius|mœbius|möbius|mobius)(?! strip)', r'jean giraud'],
 'James Gurney': [r'gurney'], 'Ross Tran': [r'ross tran'], 'Alphonse Mucha': [r'mucha'], 'Marc Simonetti': [r'simonetti'],
 'Greg Rutkowski': [r'rutkowski'], 'WLOP': [r'wlop'], 'Hokusai': [r'hokusai'],
 'Zdzisław Beksiński': [r'beksi[nń]s?k?ki', r'beksinkski'], 'Wes Anderson': [r'wes anderson'], 'Norman Rockwell': [r'norman rockwell'],
 'Gustav Klimt': [r'klimp?t'], 'Tom Bagshaw': [r'bagshaw'], 'Makoto Shinkai': [r'shinkai'], 'Yoshitaka Amano': [r'yoshitaka amano'],
 'Rembrandt': [r'rembrandt'], 'M. C. Escher': [r'escher'], 'Loish': [r'loish'], 'Thomas Kinkade': [r'kinkade', r'kindkade'],
 'Pablo Picasso': [r'picasso'], 'Vincent van Gogh': [r'van gogh'], 'Tim Burton': [r'tim burton'], 'Beeple': [r'beeple'],
 'Ashley Wood': [r'ashley wood'], 'Hajime Sorayama': [r'sorayama'], 'Sarah Morris': [r'sarah morris'],
 'Annie Leibovitz': [r'leibovitz'], 'Karel Thole': [r'karel thole'], 'Joel Meyerowitz': [r'meyerowitz'], 'Tsutomu Nihei': [r'nihei'],
 'Renato Muccillo': [r'muccillo'], 'Ansel Adams': [r'ansel adams', r'andel adams'], 'Katsuhiro Otomo': [r'otomo'],
 'Jean-Honoré Fragonard': [r'fragonard'], 'Harumi Hironaka': [r'hironaka'], 'Kilian Eng': [r'kilian eng'],
 'Gustave Doré': [r'gustave dor[eé]'], 'Andrei Riabovitchev': [r'riabovitchev'], 'J. C. Leyendecker': [r'leyendecker'],
 'Thomas Eakins': [r'eakins'], 'Takayuki Takeya': [r'takeya'], 'Charlie Bowater': [r'bowater'], 'Yoji Shinkawa': [r'shinkawa'],
 'Tim Walker': [r'tim walker'], 'Élisabeth Vigée Le Brun': [r'vig[eé]e le ?brun'], 'Anato Finnstark': [r'finnstark'],
 'Karol Bak': [r'karol bak'], 'Emil Melmoth': [r'melmoth'], 'Vincent Di Fate': [r'di fate'], 'Roger Dean': [r'roger dean'],
 'Ivan Aivazovsky': [r'aivazovsky'], 'Krenz Cushart': [r'cushart'], 'Leonardo da Vinci': [r'da vinci'], 'Ralph McQuarrie': [r'mcquarrie'],
 'Alfred Stieglitz': [r'stieglitz'], 'Mike Mignola': [r'mignola'], 'Jordan Grimmer': [r'grimmer'], 'Edward Hopper': [r'edward hopper'],
 'Andreas Rocha': [r'andreas rocha'], 'Ralph Steadman': [r'steadman'], 'Syd Mead': [r'syd mead'], 'Mateusz Urbanowicz': [r'urbanowicz'],
 'Ruan Jia': [r'ruan jia'], 'Kelly McKernan': [r'mckernan'], 'Roger Deakins': [r'deakins'], 'Stanley Kubrick': [r'kubrick'],
 'Dan Mumford': [r'mumford'], 'Brian Froud': [r'froud'], 'Stefan Gesell': [r'gesell'], 'Jean-Michel Basquiat': [r'basquiat'],
 'Filip Hodas': [r'filip hodas'], 'Yousuf Karsh': [r'karsh'], 'Floria Sigismondi': [r'sigismondi'], 'Ron English': [r'ron english'],
 'Gregory Crewdson': [r'crewdson'], 'Martin Parr': [r'martin parr'], 'Chris Ware': [r'chris ware'], 'Mary Blair': [r'mary blair'],
 'Junji Ito': [r'junji ito'], 'Banksy': [r'banksy'], 'Caravaggio': [r'caravaggio'], 'Salvador Dalí': [r'salvador dal[ií]', r'\bdal[ií]\b'],
 'Simon Stålenhag': [r'st[aå]lenhag'], 'Frank Frazetta': [r'frazetta'], 'Andy Warhol': [r'warhol'], 'Johannes Vermeer': [r'vermeer'],
 'Jamie Hewlett': [r'hewlett'], 'Takashi Murakami': [r'murakami'], 'Alex Grey': [r'alex grey'],
 'Caspar David Friedrich': [r'caspar david friedrich'], 'Michelangelo': [r'michelangelo', r'michaelangelo'], 'William Blake': [r'william blake'],
 'Francis Bacon': [r'francis bacon'], 'Jackson Pollock': [r'pollock'], 'Zaha Hadid': [r'zaha hadid'], 'Victo Ngai': [r'victo ngai'],
 'Ilya Kuvshinov': [r'kuvshinov'], 'Bernie Wrightson': [r'wrightson'], 'Maxfield Parrish': [r'maxfield parrish'], 'Wayne Barlowe': [r'barlowe'],
 'Jakub Różalski': [r'r[oó][zż]alski'], 'Ivan Shishkin': [r'shishkin'], 'Saul Bass': [r'saul bass'], 'Ridley Scott': [r'ridley scott'],
 'Denis Villeneuve': [r'villeneuve'], 'Hieronymus Bosch': [r'hieronymus bosch', r'\bbosch\b'], 'René Magritte': [r'magritte'],
 'Edvard Munch': [r'edvard munch'], 'J. M. W. Turner': [r'william turner', r'j\.?\s?m\.?\s?w\.? turner'], 'Wassily Kandinsky': [r'kandinsky'],
 'John Singer Sargent': [r'singer sargent'], 'Philippe Druillet': [r'druillet'], 'Gerald Brom': [r'gerald brom'],
 'Robert Mapplethorpe': [r'mapplethorpe'], 'Matt Mahurin': [r'mahurin'], 'Geof Darrow': [r'geof darrow'], 'Kim Jung Gi': [r'kim jung ?gi'],
 'Jeremiah Ketner': [r'ketner'], 'Diego Gisbert Llorens': [r'gisbert llorens'], 'Michel Crête': [r'michel cr[eê]te'],
 'André Simard': [r'andr[eé] simard'], 'Gunnar Leche': [r'gunnar leche'], 'Leo Varas': [r'leo varas'], 'Okuda San Miguel': [r'okuda'],
 'Julie Taymor': [r'taymor'], 'Roger Ellis': [r'roger ellis'], 'Ivan Laliashvili': [r'laliashvili'], 'Bruce Pennington': [r'pennington'],
 'Gilbert Williams': [r'gilbert williams'], 'Jon McCoy': [r'jon mccoy'], 'William Kentridge': [r'kentridge'], 'Alex Flores': [r'alex flores'],
 'Antoine Collignon': [r'collignon'], 'Asher Brown Durand': [r'asher brown durand'], 'Yildiray Cinar': [r'cinar'],
 'Kittichai Rueangchaichan': [r'rueangchaichan'], 'Josef Albers': [r'josef albers'], 'John Howe': [r'john howe'],
 'Constantin Brâncuși': [r'brancusi', r'brâncuși'], 'Daido Moriyama': [r'moriyama'], 'Frans Masereel': [r'masereel'],
 'Chris Foss': [r'chris foss'], 'Peter Gric': [r'peter gric'], 'Adam Paquette': [r'paquette'], 'Ithell Colquhoun': [r'colquhoun'],
 'László Moholy-Nagy': [r'moholy'], 'Eadweard Muybridge': [r'muybridge'], 'Terry Gilliam': [r'gilliam'], 'Ryu Oyama': [r'ryu oyama'],
 'Kazuki Tanahashi': [r'tanahashi'], 'Toni Infante': [r'toni infante'], 'Alexis Franklin': [r'alexis franklin'], 'Don Davis': [r'don davis'],
 'Mike Allred': [r'allred'], 'Butcher Billy': [r'butcher billy'], 'Javier Arcenillas': [r'arcenillas'], 'Tyler Edlin': [r'edlin'],
 'Feng Zhu': [r'feng zhu'], 'Albert Bierstadt': [r'bierstadt'], 'Jean Delville': [r'delville'], 'Dan Witz': [r'dan witz'],
}
RX = {k: re.compile(r'(?<![a-z])(?:' + '|'.join(v) + r')(?![a-z])') for k, v in A.items()}
HITS = [[k for k, r in RX.items() if r.search(t)] for t in L]
ARTIST = [bool(h) for h in HITS]                      # Rule B: names a listed artist

Q = {
 'trending on artstation': r'trending on art ?station', 'artstation (any mention)': r'art ?station', '8k': r'\b8 ?k\b', '4k': r'\b4 ?k\b',
 'octane render': r'\boctane\b', 'unreal engine': r'\bunreal\b',
 'highly/hyper/ultra detailed': r'\b(?:highly|hyper|ultra|super|extremely|very|insanely)[ -]?detail(?:ed)?\b', 'intricate': r'\bintricate',
 'hyperrealistic / photorealistic': r'\b(?:hyper|ultra|super|photo)[ -]?real(?:istic|ism)?\b', 'realistic (any)': r'\breal(?:istic|ism)\b',
 'cinematic': r'\bcinematic', 'volumetric lighting': r'\bvolumetric', 'cgsociety': r'\bcg ?society\b', 'sharp focus': r'\bsharp focus',
 'masterpiece': r'\bmasterpiece', 'award winning': r'\baward[ -]winning', 'hdr / uhd': r'\b(?:hdr|uhd)\b',
 'high resolution / high quality': r'\bhigh[ -](?:res|resolution|quality|definition)\b', 'ray tracing': r'\bray[ -]?trac',
 'vray / redshift / blender / c4d / houdini': r'\b(?:v-?ray|redshift|blender|c4d|cinema ?4d|houdini)\b',
 'depth of field / dof / bokeh': r'\b(?:depth of field|dof|bokeh)\b', 'beautiful': r'\bbeautiful', 'epic': r'\bepic\b',
}
QH = {k: [bool(re.search(v, t)) for t in L] for k, v in Q.items()}
CORE = ['trending on artstation', '8k', '4k', 'octane render', 'unreal engine', 'highly/hyper/ultra detailed',
        'hyperrealistic / photorealistic', 'volumetric lighting', 'cgsociety', 'sharp focus', 'masterpiece', 'award winning',
        'hdr / uhd', 'high resolution / high quality', 'ray tracing', 'vray / redshift / blender / c4d / houdini']
QUAL = [any(QH[k][i] for k in CORE) for i in range(len(P))]   # any core quality booster


def q4():
    print('\n' + '=' * 30, 'q4 artists and quality phrases', '=' * 30)
    n = len(P); pct = lambda k: f"{k:6d} {k/n:6.1%}"
    # Step 1 (exploration used to build the artist list): what follows "by" / "style of"?
    trig = re.compile(r"(style of|styled after|inspired by|in the manner of|\bby)\s+(.+?)(?=[,.;:|()\[\]!?]|\s+(?:and|with|in|on|at|for|from|as|style|artstation|trending)\b|$)")
    prev = Counter(); Cby = Counter(); Cst = Counter()
    for t in L:
        for m in trig.finditer(t):
            nm = m.group(2).strip()[:40]; pw = t[:m.start()].split()[-1:]
            if m.group(1) == 'by': prev[pw[0] if pw else '^'] += 1
            (Cby if m.group(1) == 'by' else Cst)[nm] += 1
    print("words before 'by':", prev.most_common(40))
    print("after by:", Cby.most_common(60))
    print("after style of etc:", Cst.most_common(60))
    # Step 2: audit ambiguous aliases
    random.seed(2); Llow = [t.lower() for t in P]
    for a in [r'mobius', r'm[oö]e?bius strip', r'\bbosch\b', r'hewlett', r'\bmucha\b', r'murakami', r'pollock', r'\bdal[ií]\b', r'monet', r'escher']:
        m = [t for t in Llow if re.search(r'(?<![a-z])(?:' + a + r')(?![a-z])', t)]
        print(f"audit {a:20s}{len(m):5d}", [x[max(0, re.search(a, x).start() - 35):re.search(a, x).end() + 15] for x in random.sample(m, min(3, len(m)))])
    # Rule A: style-attribution wording
    s1 = [bool(R_STYLE.search(t)) for t in L]; s2 = [bool(R_BY.search(t)) for t in L]; r1 = [a or b for a, b in zip(s1, s2)]
    print("R1a 'style of' etc", pct(sum(s1))); print("R1b art-word/punct + 'by <word>'", pct(sum(s2))); print("R1 either", pct(sum(r1)))
    # Rule B: named artist
    has = ARTIST
    print("artists in list", len(A)); print("R2 names a listed artist", pct(sum(has)))
    cnt = Counter(k for h in HITS for k in h)
    for i, (k, v) in enumerate(cnt.most_common(30)): print(f"  {i+1:2d}. {k:28s}{v:5d} {v/n:6.2%}")
    nart = Counter(len(h) for h in HITS if h)
    print("2+ artists share", round(sum(v for k, v in nart.items() if k >= 2) / sum(has) * 100, 1))
    print("R1 or R2", pct(sum(a or b for a, b in zip(r1, has))), "| R1 and R2", pct(sum(a and b for a, b in zip(r1, has))),
          "| R1 only", pct(sum(a and not b for a, b in zip(r1, has))), "| R2 only", pct(sum(b and not a for a, b in zip(r1, has))))
    random.seed(7)
    print("R1 without listed artist samples:"); [print('   ', x[:140]) for x in random.sample([p for p, a, b in zip(P, r1, has) if a and not b], 20)]
    ST = {'Studio Ghibli': r'ghibli', 'Pixar': r'pixar', 'Disney': r'disney', 'Marvel': r'marvel', 'Dreamworks': r'dreamworks'}
    print("studios", [(k, sum(bool(re.search(v, t)) for t in L)) for k, v in ST.items()])
    # Quality phrases
    print("quality phrases")
    for k, v in sorted(QH.items(), key=lambda x: -sum(x[1])): print(f"  {k:42s}{pct(sum(v))}")
    print("ANY core quality booster", pct(sum(QUAL)))
    print("any of trending/8k/octane", pct(sum(QH['trending on artstation'][i] or QH['8k'][i] or QH['octane render'][i] for i in range(n))))
    print("boosters per prompt", sorted(Counter(sum(QH[k][i] for k in CORE) for i in range(n)).items()))
    print("booster share: artist prompts vs others", round(sum(a and q for a, q in zip(has, QUAL)) / sum(has) * 100, 1),
          round(sum((not a) and q for a, q in zip(has, QUAL)) / (n - sum(has)) * 100, 1))


# =====================================================================================
# q5: topic models
# =====================================================================================
def tm_prep(mode):
    from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
    def clean(t):
        t = t.lower()
        t = re.sub(r'(?:--|—|–)\s?[a-z]+(?:\s+[\w:.]+)?', ' ', t)   # parameters + value
        t = re.sub(r'<?https?://\S+>?', ' ', t)                     # urls
        t = re.sub(r'::-?[\d.]*', ' ', t)                            # prompt weights
        t = re.sub(r"[^a-z\u00c0-\u024f' ]+", ' ', t)                # letters only
        return ' '.join(t.split())
    docs = [d for d in dict.fromkeys(clean(t) for t in P) if d]      # collapse prompts identical after cleaning; drop empty
    STOP = set(ENGLISH_STOP_WORDS | {'imagine', 'img', 'jpg', 'png', 'way', 'like', 'make', 'made', 'using', 'use'})
    if mode == 'subject':   # remove style/quality boilerplate and artist names so topics reflect subject matter
        STYLE = '''style styled styles art arts artwork artist artists painting paintings painted paint render rendered rendering renders
        detailed detail details detailing highly hyper ultra super extremely insanely intricate intricately realistic realism hyperrealistic hyperrealism
        photorealistic photoreal photorealism photo photograph photography photographic cinematic cinematography lighting lit light lights high
        resolution quality definition hd hdr uhd fhd octane unreal engine cgsociety artstation trending vray redshift blender houdini zbrush
        volumetric concept illustration illustrated digital beautiful epic stunning amazing masterpiece award winning sharp focus dof depth field
        bokeh blur mm lens shot camera wide angle view composition symmetrical symmetry centered thirds rule ray tracing raytracing global
        illumination subsurface scattering post processing processing matte vector flat poster wallpaper design color colors colour colours
        colorful palette dramatic moody atmosphere atmospheric soft sharp mood award tone tones texture textures quality detailing aesthetic
        background scene image picture full length close closeup up ultrarealistic realistically hyperdetailed ultradetailed render'''.split()
        NAMES = {w for k in A for w in re.findall(r"[a-z\u00e0-\u024f]+", k.lower()) if len(w) > 2} | \
                {'mullins', 'mohrbacher', 'ghibli', 'studio', 'pixar', 'disney', 'giger', 'mucha', 'kinkade'}
        NAMES -= {'wood', 'grey', 'bacon', 'hopper', 'english', 'ware', 'bass', 'blake', 'dean', 'frank', 'walker', 'adams',
                  'morris', 'davis', 'howe', 'jean', 'ellis', 'williams', 'turner', 'gogh', 'grimmer', 'parr', 'bak', 'fate', 'leche',
                  'tran', 'eng', 'jia', 'zhu', 'witz', 'bowater', 'billy', 'butcher', 'flores', 'scott', 'bosch', 'mead', 'foss',
                  'friedrich', 'david', 'caspar', 'mary', 'john', 'saul', 'alex', 'don', 'mike', 'roger', 'tim', 'tom', 'james'}
        STOP |= set(STYLE) | NAMES
    STOP = list(STOP)
    TOK = r"(?u)\b[a-z\u00c0-\u024f][a-z\u00c0-\u024f']+\b"
    tfidf = TfidfVectorizer(stop_words=STOP, token_pattern=TOK, ngram_range=(1, 2), min_df=15, max_df=0.4, sublinear_tf=True)
    X = tfidf.fit_transform(docs)
    print(f'[{mode}] distinct prompts', len(P), '-> distinct after cleaning', len(docs),
          '| tfidf', X.shape, '| docs with no vocab terms', int((X.getnnz(axis=1) == 0).sum()))
    return docs, X, tfidf.get_feature_names_out(), STOP, TOK


def tm_select(X):
    """Scan K: NPMI coherence (first run) + seed stability (mean matched top-10 Jaccard over 6 seeds)."""
    import numpy as np
    from sklearn.decomposition import NMF
    from scipy.optimize import linear_sum_assignment
    from joblib import Parallel, delayed
    Xbin = (X > 0).astype('float32').tocsc(); Nd = Xbin.shape[0]; df1 = np.asarray(Xbin.sum(axis=0)).ravel()
    def npmi(top):
        co = (Xbin[:, top].T @ Xbin[:, top]).toarray(); s = []
        for i, j in itertools.combinations(range(len(top)), 2):
            pij = co[i, j] / Nd
            if pij == 0: s.append(-1); continue
            s.append(np.log(pij / ((df1[top[i]] / Nd) * (df1[top[j]] / Nd))) / -np.log(pij))
        return float(np.mean(s))
    tops = lambda H, k=10: [list(np.argsort(-h)[:k]) for h in H]
    def match(Aa, Bb):
        J = np.array([[len(set(a) & set(b)) / len(set(a) | set(b)) for b in Bb] for a in Aa]); r, c = linear_sum_assignment(-J); return J[r, c]
    def fit(K, seed):
        return NMF(n_components=K, init='random', random_state=seed, max_iter=400, alpha_W=0.0, l1_ratio=0.0).fit(X).components_
    for K in [6, 8, 10, 12, 14, 16, 18, 20, 24, 28]:
        T = [tops(H) for H in Parallel(n_jobs=8)(delayed(fit)(K, s) for s in range(6))]
        coh = np.mean([npmi(t) for t in T[0]])
        stab = np.mean([match(T[i], T[j]).mean() for i, j in itertools.combinations(range(len(T)), 2)])
        print(f"K={K:3d}  NPMI={coh:.3f}  seed-stability(top10 Jaccard)={stab:.3f}", flush=True)


def tm_final(docs, X, vocab, STOP, TOK, K, NS=20):
    """Final NMF at K; medoid reference run; stability over seeds, 80% subsamples, other K, and LDA."""
    import numpy as np
    from sklearn.decomposition import NMF, LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer
    from scipy.optimize import linear_sum_assignment
    from joblib import Parallel, delayed
    def fitH(Xm, k, seed):
        m = NMF(n_components=k, init='random', random_state=seed, max_iter=1000); W = m.fit_transform(Xm); return m.components_, W
    tops = lambda H, k=10: [list(np.argsort(-h)[:k]) for h in H]
    jac = lambda a, b: len(set(a) & set(b)) / len(set(a) | set(b))
    def match(TA, TB):
        J = np.array([[jac(a, b) for b in TB] for a in TA]); r, c = linear_sum_assignment(-J); m = np.zeros(len(TA), int); m[r] = c
        return m, J[np.arange(len(TA)), m]
    def best(TA, TB): return np.array([[jac(a, b) for b in TB] for a in TA]).max(axis=1)
    def dominant(W):
        d = W.argmax(1); d[W.sum(1) == 0] = -1; return d
    print(f"\n----- final model K={K}")
    seed_runs = Parallel(n_jobs=10)(delayed(fitH)(X, K, s) for s in range(NS))
    T = [tops(H) for H, _ in seed_runs]
    pair = np.zeros((NS, NS))
    for i, j in itertools.combinations(range(NS), 2): pair[i, j] = pair[j, i] = match(T[i], T[j])[1].mean()
    ref = int(pair.sum(1).argmax()); Wref = seed_runs[ref][1]; Tref = T[ref]
    print(f"reference run seed={ref}; mean pairwise topic-match across {NS} seeds = {pair[np.triu_indices(NS, 1)].mean():.3f}")
    dom_ref = dominant(Wref)
    seed_j = np.array([match(Tref, T[s])[1] for s in range(NS) if s != ref])
    agree, share_runs = [], []
    for s in range(NS):
        if s == ref: continue
        m, _ = match(Tref, T[s]); inv = {c: r for r, c in enumerate(m)}
        d2 = np.array([inv.get(x, -2) if x >= 0 else -1 for x in dominant(seed_runs[s][1])])
        agree.append((d2 == dom_ref).mean()); share_runs.append([(d2 == k).mean() for k in range(K)])
    share_runs = np.array(share_runs)
    def sub(seed):
        idx = np.random.default_rng(1000 + seed).choice(X.shape[0], int(.8 * X.shape[0]), replace=False)
        return tops(fitH(X[idx], K, seed)[0])
    boot_j = np.array([match(Tref, b)[1] for b in Parallel(n_jobs=10)(delayed(sub)(s) for s in range(NS))])
    nk_j = {k: best(Tref, tops(fitH(X, k, 0)[0])) for k in (12, 16, 20, 24)}
    C = CountVectorizer(vocabulary=vocab, ngram_range=(1, 2), token_pattern=TOK, stop_words=STOP).fit_transform(docs)
    def lda(s):
        return LatentDirichletAllocation(n_components=K, learning_method='online', random_state=s, max_iter=20, batch_size=2048).fit(C).components_
    lda_T = [tops(H) for H in Parallel(n_jobs=5)(delayed(lda)(s) for s in range(5))]
    lda_j = np.array([match(Tref, t)[1] for t in lda_T])
    lda_self = np.mean([match(lda_T[i], lda_T[j])[1].mean() for i, j in itertools.combinations(range(5), 2)])
    print(f"docs={len(docs)}; unassigned = {(dom_ref == -1).sum()} ({(dom_ref == -1).mean():.1%})")
    print(f"doc-level: same dominant topic as reference run, mean over seeds = {np.mean(agree):.1%} (min {np.min(agree):.1%})")
    print(f"overall top-10 Jaccard: seeds {seed_j.mean():.3f} | 80% subsamples {boot_j.mean():.3f} | LDA {lda_j.mean():.3f} (LDA vs itself {lda_self:.3f})")
    random.seed(5)
    for k in np.argsort(-np.array([(dom_ref == k).mean() for k in range(K)])):
        print(f"\nT{k:02d} share={(dom_ref == k).mean():6.1%} (seed range {share_runs[:, k].min():.1%}-{share_runs[:, k].max():.1%}) "
              f"| Jaccard seeds {seed_j[:, k].mean():.2f} (min {seed_j[:, k].min():.2f}) subs {boot_j[:, k].mean():.2f} "
              f"| found at K=12/16/20/24: {' '.join(f'{nk_j[q][k]:.2f}' for q in (12, 16, 20, 24))} | LDA {lda_j[:, k].mean():.2f}")
        print('   words:', ', '.join(vocab[i] for i in Tref[k]))
        for e in random.sample([docs[i] for i in np.where(dom_ref == k)[0]], 4): print('   eg:', e[:110])
    print("\nLDA topics (seed 0):")
    for t in lda_T[0]: print('  ', ', '.join(vocab[i] for i in t[:8]))


def q5():
    print('\n' + '=' * 30, 'q5 topic models', '=' * 30)
    print("\n### Model A: all words")
    d, X, v, S, T = tm_prep('style'); tm_select(X); tm_final(d, X, v, S, T, K=18)
    print("\n### Model B: style/quality words and artist names removed")
    d, X, v, S, T = tm_prep('subject'); tm_select(X); tm_final(d, X, v, S, T, K=10); tm_final(d, X, v, S, T, K=16)


# =====================================================================================
# q6: hypothesis tests
# =====================================================================================
def q6():
    import numpy as np
    from scipy import stats
    print('\n' + '=' * 30, 'q6 hypothesis tests', '=' * 30)
    rng = np.random.default_rng(0); n = len(P)
    param = np.array([bool(re.search(r'(?:^|\s)(?:--|—|–)\s?[A-Za-z]', t)) for t in P])
    length = np.array([len(words(leftover(t))) for t in P])        # descriptive words, params removed
    total_len = np.array([len(t.split()) for t in P])
    artist = np.array(ARTIST); qual = np.array(QUAL)

    def h1(mask=slice(None), lab='all'):
        a, b = length[mask][param[mask]], length[mask][~param[mask]]
        U, p = stats.mannwhitneyu(a, b, alternative='greater')
        ps = U / (len(a) * len(b)); rb = 2 * ps - 1
        hl = np.median(rng.choice(a, 400000) - rng.choice(b, 400000))
        t, pt = stats.ttest_ind(a, b, equal_var=False, alternative='greater')
        sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2)); d = (a.mean() - b.mean()) / sp
        bs = [np.median(rng.choice(a, len(a))) - np.median(rng.choice(b, len(b))) for _ in range(1000)]
        print(f"[H1 {lab}] n_param={len(a)} n_none={len(b)} | median {np.median(a):.0f} vs {np.median(b):.0f} "
              f"(diff 95% CI {np.percentile(bs, 2.5):.0f} to {np.percentile(bs, 97.5):.0f}) | mean {a.mean():.2f} vs {b.mean():.2f}")
        print(f"      Mann-Whitney U={U:.4g}, one-sided p={p:.3g} | P(superiority)={ps:.3f}, rank-biserial r={rb:.3f}, "
              f"HL shift={hl:.1f} words | Welch t={t:.1f}, p={pt:.3g}, Cohen d={d:.2f}")
        allv = np.concatenate([a, b]); _, cnt = np.unique(allv, return_counts=True); n1, n2 = len(a), len(b); Nn = n1 + n2
        sig = np.sqrt(n1 * n2 / 12 * ((Nn + 1) - (cnt**3 - cnt).sum() / (Nn * (Nn - 1))))
        z = (U - n1 * n2 / 2) / sig
        print(f"      tie-corrected z = {z:.1f}; log10 p = {stats.norm.logsf(z) / np.log(10):.0f}")

    def tab(x, y): return np.array([[np.sum(x & y), np.sum(x & ~y)], [np.sum(~x & y), np.sum(~x & ~y)]])

    def h2(mask=slice(None), lab='all'):
        T = tab(artist[mask], qual[mask]); (a, b), (c, d) = T; p1, p0 = a / (a + b), c / (c + d)
        chi2, pc, _, _ = stats.chi2_contingency(T, correction=False)
        OR, pf = stats.fisher_exact(T, alternative='greater')
        ci = np.exp(np.log(OR) + np.array([-1.96, 1.96]) * np.sqrt(1/a + 1/b + 1/c + 1/d))
        rd = p1 - p0; rd_se = np.sqrt(p1 * (1 - p1) / (a + b) + p0 * (1 - p0) / (c + d))
        rr = p1 / p0; rrci = np.exp(np.log(rr) + np.array([-1.96, 1.96]) * np.sqrt(1/a - 1/(a + b) + 1/c - 1/(c + d)))
        phi = np.sqrt(chi2 / T.sum())
        z = rd / np.sqrt(((a + c) / T.sum()) * (1 - (a + c) / T.sum()) * (1 / (a + b) + 1 / (c + d)))
        print(f"[H2 {lab}] table [[artist&qual, artist&no],[noartist&qual, noartist&no]] = {T.tolist()}")
        print(f"      rate: artist {p1:.1%} vs no artist {p0:.1%} | risk diff {rd*100:.1f} pts ({(rd-1.96*rd_se)*100:.1f} to {(rd+1.96*rd_se)*100:.1f}) "
              f"| risk ratio {rr:.2f} ({rrci[0]:.2f}-{rrci[1]:.2f})")
        print(f"      chi2(1)={chi2:.1f}, p={pc:.3g}, log10 p={(stats.norm.logsf(np.sqrt(chi2)) + np.log(2)) / np.log(10):.0f} | one-sided z={z:.1f} "
              f"| Fisher one-sided p={pf:.3g} | OR={OR:.2f} ({ci[0]:.2f}-{ci[1]:.2f}) | phi={phi:.3f}")

    def logit(Xs, y, names):
        Xm = np.column_stack([np.ones(len(y))] + Xs); b = np.zeros(Xm.shape[1])
        for _ in range(50):   # Newton-Raphson / IRLS
            p = 1 / (1 + np.exp(-Xm @ b)); H = Xm.T @ (Xm * (p * (1 - p))[:, None]); step = np.linalg.solve(H, Xm.T @ (y - p)); b += step
            if np.abs(step).max() < 1e-10: break
        se = np.sqrt(np.diag(np.linalg.inv(H)))
        for nm, bi, si in zip(names, b[1:], se[1:]):
            z = bi / si
            print(f"      {nm:26s} OR={np.exp(bi):.2f} ({np.exp(bi-1.96*si):.2f}-{np.exp(bi+1.96*si):.2f}), z={z:.1f}, p={2*stats.norm.sf(abs(z)):.3g}")

    def mh(lenvar, label):
        num = den = Ssum = Vsum = 0
        for lo, hi in [(1, 5), (6, 10), (11, 15), (16, 20), (21, 30), (31, 50), (51, 999)]:
            m = (lenvar >= lo) & (lenvar <= hi); T = tab(artist[m], qual[m]); (a, b), (c, d) = T; Nn = T.sum()
            num += a * d / Nn; den += b * c / Nn
            Ssum += a - (a + b) * (a + c) / Nn; Vsum += (a + b) * (c + d) * (a + c) * (b + d) / (Nn * Nn * (Nn - 1))
            print(f"      {label} {lo:>2}-{hi:<3} n={Nn:6d} artist={a+b:5d}  rate artist {a/(a+b):.1%} vs none {c/(c+d):.1%}  OR={(a*d)/(b*c):.2f}")
        cmh = (abs(Ssum) - 0.5)**2 / Vsum
        print(f"      MH common OR={num/den:.2f}; CMH chi2(1)={cmh:.1f}, p={stats.chi2.sf(cmh, 1):.3g}")

    print(f"N={n}; with param {param.sum()} ({param.mean():.1%}); artist {artist.sum()} ({artist.mean():.1%}); quality {qual.sum()} ({qual.mean():.1%})")
    print("\n=== H1 main"); h1()
    def norm(t): return ' '.join(re.sub(r'[^a-z ]', ' ', re.sub(r'(?:--|—|–)\s?[a-z]+(?:\s+[\w:.]+)?', ' ', t.lower())).split())
    first = {}
    for i, t in enumerate(P): first.setdefault(norm(t), i)
    keep = np.zeros(n, bool); keep[list(first.values())] = True
    print("\n=== H1 sensitivity: near-duplicates collapsed"); h1(keep, 'dedup')
    print("=== H1 total tokens incl. params: median", np.median(total_len[param]), "vs", np.median(total_len[~param]))
    print("\n=== H2 main"); h2()
    print("\n=== H2 sensitivity: near-duplicates collapsed"); h2(keep, 'dedup')
    print("\n=== H2 controlling for length (all descriptive words)")
    logit([artist.astype(float), np.log1p(length)], qual.astype(float), ['artist', 'log(1+words)'])
    mh(length, 'words')
    print("\n=== H2 controlling for length excluding the artist-name words")
    def strip_art(t):
        for r in RX.values(): t = r.sub(' ', t)
        return t
    len2 = np.array([len(words(leftover(strip_art(l)))) for l in L])
    print("      mean words removed from artist prompts:", round((length - len2)[artist].mean(), 2))
    logit([artist.astype(float), np.log1p(len2)], qual.astype(float), ['artist', 'log(1+non-artist words)'])
    logit([artist.astype(float), np.log1p(len2), artist * np.log1p(len2)], qual.astype(float),
          ['artist', 'log(1+non-artist words)', 'artist x log(words)'])
    mh(len2, 'non-artist words')


for s in SECTIONS:
    globals()[s]()
```

How this file differs from the separate scripts I ran during the session (all checked against the original output):
- **`--stop` value counts** (q3) come from the later strict-dash rule, so there are 58 prompts with `--stop 90` rather than the 62 from the first pass. I didn't report that number.
- **q4's 29.3%** (quality-phrase rate in prompts without an artist) uses the corrected "Möbius strip" rule. One earlier printout showed 29.2%, from before that fix.
- **q6 prints two extra lines:** the exact z-value for the near-duplicate check (84.5) and the CMH test p-value for the second length control (0.83). Neither changes any conclusion.

## Notes

Two background-task notifications appear in the log during P6 (the tool's own long-running scripts finishing). No `Please continue.` prompts were sent.
