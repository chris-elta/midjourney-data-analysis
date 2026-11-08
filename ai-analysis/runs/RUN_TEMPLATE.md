# AI run <A|B|C>

- Tool / model:
- Date and time:
- Settings: memory off, custom instructions off, web search off, new chat
- File uploaded or folder opened: midjourney_prompts_all.csv (SHA-256 582e6d09...4806)
- Chat share link or export file (if available):

Paste each prompt exactly as written below, then the full, unedited
response. Include code the tool ran and any errors.

## P0

**Prompt:**

> I have uploaded a dataset of text-to-image prompts collected from the Midjourney Discord server. Analyse this dataset and report your main findings.

**Response:**

## P1

**Prompt:**

> How clean is this dataset? Report how many rows are empty, duplicated, or are not real prompts, and whether rows in the validation and test splits also appear in the train split. Explain exactly how you decided what counts as "not a real prompt".

**Response:**

## P2

**Prompt:**

> Excluding rows that are not real prompts and removing duplicates, describe what a typical prompt looks like: its length in words, how often Midjourney parameters such as --ar, --no, --w/--h, --stop and --seed are used, and the most common aspect ratios.

**Response:**

## P3

**Prompt:**

> What share of prompts reference a named artist or "in the style of" someone? Which artists are named most often? What share use generic quality phrases such as "trending on artstation", "8k" or "octane render"? State the rule you used to detect each.

**Response:**

## P4

**Prompt:**

> Identify the main themes or topics in the prompts using a topic model. Report the topics with their top words and the share of prompts in each. How stable are these topics if the analysis is re-run?

**Response:**

## P5

**Prompt:**

> Test two hypotheses and report the test, test statistic, p-value and an effect size for each: (H1) prompts that use at least one parameter are longer than prompts that use none; (H2) prompts that name an artist are more likely to use a quality phrase.

**Response:**

## P6

**Prompt:**

> Give me the complete code you ran for all of the above, in one block, so that I can reproduce your results.

**Response:**

## Notes

Errors, timeouts, "Please continue." prompts, anything unusual.
