# Analysis log

- **Tool / model:** GitHub Copilot, Copilot SDK agent in VS Code; model ID recorded in the export: `agent-host-copilotcli:gpt-6.1-terra`.
- **Date and time:** conversation began 2026-11-08 12:12:07 UTC−07:00; individual exported request timestamps are given below. This log was created on 2026-11-08.
- **Settings:** memory off, custom instructions off, web search off, new chat (as stated by the user; not independently verified from the export).
- **File uploaded or folder opened:** `midjourney_prompts_all.csv`; SHA-256 `582e6d0977c554135f231e1e03d806535aa4755d61f3425c49ca6bfe28934806`, verified locally.
- **Chat share link or export file:** [run-A.json](./run-A.json); no share link provided.

The first seven requests, response text, terminal commands and available terminal outputs below come from the export. Interim assistant messages and final responses are included in order. Internal reasoning is not included. Outputs marked as offloaded are reproduced from the referenced local temporary files where available. Nonterminal tool inputs or outputs not stored in the export cannot be reconstructed. The two later requests and final responses are transcribed from the current conversation; their tool calls were not present in the earlier JSON export. The current request to create this log is not included as a completed exchange.

## Exchange 1

**Request time:** 2026-11-08T12:12:07.261000-07:00

### Prompt

```text
I have uploaded a dataset of text-to-image prompts collected from the Midjourney Discord server. Analyse this dataset and report your main findings.
```

### Response and recorded tool activity

I’ll inspect the dataset’s structure and quality first, then quantify the main patterns in the prompts and note any limits on interpretation.

**Tool: bash — Inspect dataset size, schema, and initial records**

Command:

```bash
ls -lh midjourney_prompts_all.csv; file midjourney_prompts_all.csv; python - <<'PY'
import csv
p='midjourney_prompts_all.csv'
with open(p, encoding='utf-8-sig', newline='') as f:
    r=csv.reader(f)
    for i, row in enumerate(r):
        print(i, repr(row)[:2000])
        if i >= 4: break
PY
```

Exit code: 127

Recorded output:

```text
-rw-rw-r-- 1 elta elta 18M Nov  8 12:03 midjourney_prompts_all.csv
midjourney_prompts_all.csv: CSV text
/bin/bash: python: command not found
```

**Tool: bash — Inspect CSV schema and initial records**

Command:

```bash
python3 - <<'PY'
import csv
p='midjourney_prompts_all.csv'
with open(p, encoding='utf-8-sig', newline='') as f:
    r=csv.reader(f)
    for i, row in enumerate(r):
        print(i, repr(row)[:2000])
        if i >= 4: break
PY
```

Exit code: 0

Recorded output:

```text
0 ['split', 'text']
1 ['train', 'York']
2 ['train', 'render']
3 ['train', 'Tmmy lee Jones super realistic detailed beautiful detailed portrait --test --ar 8:10']
4 ['train', 'a beautiful rendition of the god of jelly fishes machines, thousands of acid flowers, high voltage magic, ornate, arcane electricity, complex scene , highly detailed. --w 2160 --h 3840']
```

**Tool: bash — Measure dataset coverage, duplicates, prompt lengths, parameters, and common language**

Command:

```bash
python3 - <<'PY'
import csv, collections, re, statistics, math, hashlib
p='midjourney_prompts_all.csv'
with open(p, encoding='utf-8-sig', newline='') as f:
    rows=list(csv.DictReader(f))
n=len(rows); print('ROWS',n,'SPLITS',collections.Counter(r['split'] for r in rows))
texts=[r['text'] for r in rows]; nonempty=[t for t in texts if t.strip()]; print('NONEMPTY',len(nonempty),'EMPTY',n-len(nonempty))
counts=collections.Counter(texts); norm=collections.Counter(re.sub(r'\s+',' ',t.strip().casefold()) for t in texts); print('EXACT_UNIQUE',len(counts),'EXACT_DUP_EXTRA',n-len(counts),'NORM_UNIQUE',len(norm),'NORM_DUP_EXTRA',n-len(norm),'DUP_GROUPS',sum(v>1 for v in counts.values()),'ROWS_IN_DUP_GROUPS',sum(v for v in counts.values() if v>1),'MAX_MULTIPLICITY',max(counts.values()))
for t,c in counts.most_common(10): print('DUP',c,repr(t[:160]))
for split in sorted(set(r['split'] for r in rows)):
    ts=[r['text'] for r in rows if r['split']==split]; print('SPLIT',split,'n',len(ts),'unique',len(set(ts)),'empty',sum(not t.strip() for t in ts))
splits={s:set(r['text'] for r in rows if r['split']==s) for s in set(r['split'] for r in rows)}
for a in sorted(splits):
 for b in sorted(splits):
  if a<b: print('SPLIT_OVERLAP',a,b,len(splits[a]&splits[b]))
wordpat=re.compile(r"[a-z]+(?:['’][a-z]+)?|\d+", re.I)
lengths=[len(wordpat.findall(t)) for t in nonempty]; chars=[len(t) for t in nonempty]
def desc(name, v):
 v=sorted(v); print(name,'mean',round(statistics.mean(v),2),'median',statistics.median(v),'p10',v[int(.1*(len(v)-1))],'p90',v[int(.9*(len(v)-1))],'p99',v[int(.99*(len(v)-1))],'max',v[-1])
desc('WORDS',lengths); desc('CHARS',chars)
print('WORD_LEN_BINS',[(x,sum(a<=v<b for v in lengths)) for x,a,b in [('1-5',0,6),('6-10',6,11),('11-20',11,21),('21-50',21,51),('51-100',51,101),('101+',101,10**9)]])
param_re=re.compile(r'(?<!\S)--([a-z][a-z0-9-]*)',re.I)
params=collections.Counter(); param_occ=collections.Counter(); withp=0
for t in nonempty:
 ps=[x.lower() for x in param_re.findall(t)]; params.update(set(ps));param_occ.update(ps);withp+=bool(ps)
print('WITH_PARAMS',withp);print('PARAM_DOC',params.most_common(40)); print('PARAM_OCC',param_occ.most_common(20))
for k in ['ar','aspect','v','version','stylize','s','q','quality','chaos','c','seed','w','h','test','testp','niji','no','stop','uplight','upbeta','hd','video','iw']:
 rx=re.compile(r'(?<!\S)--'+k+r'\b(?:\s+([^\s,]+))?',re.I); vals=collections.Counter()
 for t in nonempty:
  m=rx.search(t)
  if m: vals[m.group(1) or '<none>']+=1
 if vals: print('PARAM_VAL',k,vals.most_common(12))
# Token and phrase frequencies exclude parameters and their trailing values by treating the first parameter as the end of the prompt body.
stop=set('a an the and or of in on for to with as is at by from that this it its into out up i my me we our you your be are was were very so but not no has have one two three four five all over under through using use made make image picture photo art style high highly detailed detail realistic ultra'.split())
unigram=collections.Counter(); bigram=collections.Counter(); trigram=collections.Counter(); raw=collections.Counter()
for t in nonempty:
 body=re.split(r'(?<!\S)--[a-z]',t,maxsplit=1,flags=re.I)[0].lower(); words=re.findall(r"[a-z]+(?:['’][a-z]+)?",body)
 raw.update(set(words)); unigram.update(set(w for w in words if w not in stop and len(w)>1)); bigram.update(set(zip(words,words[1:]))); trigram.update(set(zip(words,words[1:],words[2:])))
print('RAW_DOC_WORDS',raw.most_common(50));print('CONTENT_DOC_WORDS',unigram.most_common(70));print('BIGRAM_DOC',bigram.most_common(45)); print('TRIGRAM_DOC',trigram.most_common(30))
PY
```

Exit code: 0

Recorded output:

```text
Output too large to read at once (8.3 KB). Saved to: /tmp/1794165173032-copilot-tool-output-7333-0a015e05-f125-4ba4-af0c-91b24fbfc8c4.txt
Consider using tools like rg (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
ROWS 246381 SPLITS Counter({'train': 221743, 'test': 12320, 'validation': 12318})
NONEMPTY 244784 EMPTY 1597
EXACT_UNIQUE 65398 EXACT_DUP_EXTRA 180983 NORM_UNIQUE 65112 NORM_DUP_EXTRA 181269 DUP_GROUPS 27453 ROWS_IN_DUP_GROUPS 208436 MAX_MULTIPLICITY 12470
DUP 12470 '16:9'
DUP 9969 '--uplight'
DUP 4662 '9:16'
DUP 2479 '2:3'
DUP 2054 '1920'
DUP 1851 'render'
DUP 1597 ''
DUP 1424 '3:4'
DUP 1391 '1'
DUP 1082 '4:5'
SPLIT test n 12320 unique 7150 empty 71
SPLIT train n 221743 unique 61505 empty 1436
```

The referenced offloaded output is no longer available.

**Tool: view — Read tool output**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Tool: view — Read tool output**

The export does not contain a complete input/output transcript for this nonterminal tool call.

The initial results show substantial repetition and many short fragments, so I’m separating dataset-quality findings from patterns that remain visible in longer, deduplicated text.

**Tool: bash — Assess leakage, short fragments, duplicate concentration, and deduplicated prompt patterns**

Command:

```bash
python3 - <<'PY'
import csv,re,collections,statistics,random
with open('midjourney_prompts_all.csv',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
wre=re.compile(r"[a-z]+(?:['’][a-z]+)?|\d+",re.I)
word=lambda t:len(wre.findall(t))
non=[r for r in rows if r['text'].strip()]; long=[r for r in non if word(r['text'])>=6]; unique=list(dict.fromkeys(r['text'] for r in long)); alluniq=list(dict.fromkeys(r['text'] for r in non))
print('COUNTS nonempty',len(non),'long6',len(long),'long_unique',len(unique),'nonempty_unique',len(alluniq))
for label,rs in [('all',rows),('nonempty',non),('long6',long)]:
 train={r['text'] for r in rs if r['split']=='train'}
 for s in ['test','validation']:
  sub=[r for r in rs if r['split']==s]; hit=[r for r in sub if r['text'] in train]; u=set(r['text'] for r in sub)
  print('LEAK',label,s,'rows',len(sub),'overlap_rows',len(hit),'overlap_unique',len(u&train),'unique_total',len(u))
counts=collections.Counter(r['text'] for r in long)
for t,c in counts.most_common(12):print('LONG_DUP',c,repr(t[:300]))
for label,ts in [('all_nonempty',[r['text'] for r in non]),('long_rows',[r['text'] for r in long]),('long_unique',unique)]:
 print('\nSET',label,len(ts))
 pats={
 'url':r'https?://\S+',
 'has_any_doublehyphen_parameter':r'(?<!\S)--[a-z]',
 'aspect_alone':r'^\s*\d+\s*:\s*\d+\s*$',
 'parameter_alone':r'^\s*--[a-z][a-z0-9-]*\s*$',
 'single_number':r'^\s*\d+(?:\.\d+)?\s*$',
 'highly detailed':r'\bhighly\s+detailed\b',
 'octane render':r'\boctane\s+render\b',
 'unreal engine':r'\bunreal\s+engine\b',
 'trending on artstation':r'\btrending\s+on\s+artstation\b',
 'cinematic':r'\bcinematic\b',
 'portrait':r'\bportraits?\b',
 'landscape':r'\blandscapes?\b',
 'city':r'\bcit(?:y|ies)\b',
 'fantasy':r'\bfantasy\b',
 'cyberpunk':r'\bcyberpunk\b',
 'photorealistic':r'\bphotorealistic\b',
 'style of':r'\bstyle\s+of\b',
 'craig mullins':r'\bcraig\s+mullins\b',
 'peter mohrbacher':r'\bpeter\s+mohrbacher\b',
 }
 for k,p in pats.items():
  rx=re.compile(p,re.I); v=sum(bool(rx.search(t)) for t in ts);print('PAT',k,v,f'{100*v/len(ts):.2f}%')
 params=collections.Counter()
 for t in ts:params.update(set(x.lower() for x in re.findall(r'(?<!\S)--([a-z][a-z0-9-]*)',t,re.I)))
 print('PARAMS',params.most_common(12))
 big=collections.Counter(); tri=collections.Counter()
 for t in ts:
  body=re.split(r'(?<!\S)--[a-z]',t,maxsplit=1,flags=re.I)[0].lower(); tokens=re.findall(r"[a-z]+(?:['’][a-z]+)?|\d+[a-z]*",body)
  big.update(set(zip(tokens,tokens[1:])));tri.update(set(zip(tokens,tokens[1:],tokens[2:])))
 print('BIG',big.most_common(20)); print('TRI',tri.most_common(15))
print('\nRANDOM NONEMPTY', )
random.seed(3)
for r in random.sample(non,20): print(repr(r['text'][:250]))
PY
```

Exit code: 0

Recorded output:

```text
Output too large to read at once (9.0 KB). Saved to: /tmp/1794165221672-copilot-tool-output-7333-db343777-88ca-4679-be83-e7da680f37a9.txt
Consider using tools like rg (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
COUNTS nonempty 244784 long6 109678 long_unique 51451 nonempty_unique 65397
LEAK all test rows 12320 overlap_rows 10239 overlap_unique 5114 unique_total 7150
LEAK all validation rows 12318 overlap_rows 10365 overlap_unique 5092 unique_total 7013
LEAK nonempty test rows 12249 overlap_rows 10168 overlap_unique 5113 unique_total 7149
LEAK nonempty validation rows 12228 overlap_rows 10275 overlap_unique 5091 unique_total 7012
LEAK long6 test rows 5516 overlap_rows 3851 overlap_unique 3353 unique_tot
```

The referenced offloaded output is no longer available.

**Tool: view — Read tool output**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Tool: view — Read tool output**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Tool: bash — Cross-check unique-text themes and aspect ratios including alternate dash characters**

Command:

```bash
python3 - <<'PY'
import csv,re,collections,statistics
with open('midjourney_prompts_all.csv',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
w=re.compile(r"[a-z]+(?:['’][a-z]+)?|\d+",re.I)
ts=list(dict.fromkeys(r['text'] for r in rows if len(w.findall(r['text']))>=6))
print('LONG_UNIQUE_LENGTH', 'median',statistics.median(len(w.findall(t)) for t in ts),'mean',round(statistics.mean(len(w.findall(t)) for t in ts),2))
for pat in [r'(?<!\S)--[a-z]',r'(?<!\S)[—–][a-z]',r'(?<!\S)(?:--|[—–])(?:ar|aspect)\s+\d+\s*:\s*\d+',r'\b(?:oil painting|watercolou?r|illustration|painting|sketch|drawing)\b',r'\b(?:photo|photography|photograph|photorealistic|photorealism|photoreal|realistic)\b',r'\b(?:cinematic|lighting|render|octane|unreal engine)\b',r'\b(?:portrait|portraits|face|woman|man|character|person|people)\b',r'\b(?:fantasy|sci[ -]?fi|cyberpunk|futuristic)\b']:
 print('PAT',pat, sum(bool(re.search(pat,t,re.I)) for t in ts))
counts=collections.Counter(); orient=collections.Counter(); bad=0
for t in ts:
 m=re.search(r'(?<!\S)(?:--|[—–])(?:ar|aspect)\s+(\d+)\s*:\s*(\d+)',t,re.I)
 if m:
  a,b=map(int,m.groups())
  if b==0 or a==0: bad+=1;continue
  counts[f'{a}:{b}']+=1
  orient['landscape' if a>b else 'portrait' if a<b else 'square']+=1
print('ASPECT',sum(orient.values()),orient,counts.most_common(12),'bad',bad)
print('SPLITPCTS',[(s,round(100*sum(r['split']==s for r in rows)/len(rows),2)) for s in ('train','test','validation')])
PY
```

Exit code: 0

Recorded output:

```text
LONG_UNIQUE_LENGTH median 16 mean 20.42
PAT (?<!\S)--[a-z] 23304
PAT (?<!\S)[—–][a-z] 3821
PAT (?<!\S)(?:--|[—–])(?:ar|aspect)\s+\d+\s*:\s*\d+ 20488
PAT \b(?:oil painting|watercolou?r|illustration|painting|sketch|drawing)\b 7254
PAT \b(?:photo|photography|photograph|photorealistic|photorealism|photoreal|realistic)\b 12052
PAT \b(?:cinematic|lighting|render|octane|unreal engine)\b 14138
PAT \b(?:portrait|portraits|face|woman|man|character|person|people)\b 8200
PAT \b(?:fantasy|sci[ -]?fi|cyberpunk|futuristic)\b 4795
ASPECT 20488 Counter({'landscape': 11096, 'portrait': 9275, 'square': 117}) [('16:9', 6714), ('9:16', 2463), ('2:3', 1493), ('4:5', 817), ('16:8', 687), ('3:4', 592), ('11:17', 538), ('3:2', 465), ('2:1', 432), ('7:5', 387), ('4:3', 383), ('21:9', 337)] bad 0
SPLITPCTS [('train', 90.0), ('test', 5.0), ('validation', 5.0)]
```

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


## Exchange 2

**Request time:** 2026-11-08T12:22:40.500000-07:00

### Prompt

```text
How clean is this dataset? Report how many rows are empty, duplicated, or are not real prompts, and whether rows in the validation and test splits also appear in the train split. Explain exactly how you decided what counts as "not a real prompt".
```

### Response and recorded tool activity

I’ll use an explicit, conservative rule for identifying non-prompt rows, and report it separately from duplicates and split overlap so those categories aren’t mistaken for disjoint totals.

**Tool: bash — Calculate exact cleaning categories and train-split overlap with reproducible rules**

Command:

```bash
python3 - <<'PY'
import csv,re,collections,statistics
p='midjourney_prompts_all.csv'
with open(p, encoding='utf-8-sig', newline='') as f: rows=list(csv.DictReader(f))
ratio=re.compile(r'\s*\d+\s*:\s*\d+\s*')
number=re.compile(r'\s*\d+(?:\.\d+)?\s*')
parameter=re.compile(r'\s*(?:(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)(?:\s+(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)*\s*',re.I)
url=re.compile(r'\s*https?://\S+\s*',re.I)
def label(t):
 if not t.strip():return 'empty'
 if ratio.fullmatch(t):return 'ratio'
 if number.fullmatch(t):return 'number'
 if parameter.fullmatch(t):return 'parameter_only'
 if url.fullmatch(t):return 'url_only'
 return 'not_flagged'
labels=collections.Counter(label(r['text']) for r in rows)
print('LABELS',labels)
for typ in labels:
 values=collections.Counter(r['text'] for r in rows if label(r['text'])==typ)
 print('LABEL_DETAILS',typ,'rows',sum(values.values()),'unique',len(values),'examples',[(repr(t[:100]),v) for t,v in values.most_common(12)])
for filtname,pred in [('all',lambda r:True),('nonempty',lambda r:label(r['text'])!='empty'),('not_flagged',lambda r:label(r['text'])=='not_flagged')]:
 sub=[r for r in rows if pred(r)]; counts=collections.Counter(r['text'] for r in sub)
 print('DUPS',filtname,'rows',len(sub),'unique',len(counts),'extra',len(sub)-len(counts),'duplicate_group_rows',sum(c for c in counts.values() if c>1),'duplicate_groups',sum(c>1 for c in counts.values()))
 train={r['text'] for r in sub if r['split']=='train'}
 for split in ['train','validation','test']:
  sr=[r for r in sub if r['split']==split]; su=set(r['text'] for r in sr)
  print('SPLIT',filtname,split,'rows',len(sr),'unique',len(su),'in_train_rows',sum(r['text'] in train for r in sr) if split!='train' else '-', 'in_train_unique',len(su&train) if split!='train' else '-')
print('LABELS_BY_SPLIT')
for s in ('train','validation','test'):
 print(s,collections.Counter(label(r['text']) for r in rows if r['split']==s))
print('FLAGGED_AND_DUPLICATED_ROW_COUNT',sum(label(r['text']) not in ('not_flagged','empty') and collections.Counter(x['text'] for x in rows)[r['text']]>1 for r in []))
counts=collections.Counter(r['text'] for r in rows)
print('FLAGGED_DUP_GROUP_ROWS',sum(1 for r in rows if label(r['text']) not in ('not_flagged','empty') and counts[r['text']]>1))
word=re.compile(r"[a-z]+(?:['’][a-z]+)?|\d+",re.I)
notflag=[r['text'] for r in rows if label(r['text'])=='not_flagged']
for n in [1,2,3,5]:
 print('UNFLAGGED_SHORT',n,sum(len(word.findall(t))<=n for t in notflag))
one=collections.Counter(t for t in notflag if len(word.findall(t))==1)
print('UNFLAGGED_SINGLE_TOP',one.most_common(25))
PY
```

Exit code: 0

Recorded output:

```text
LABELS Counter({'not_flagged': 183567, 'ratio': 34993, 'parameter_only': 13757, 'number': 12467, 'empty': 1597})
LABEL_DETAILS not_flagged rows 183567 unique 64907 examples [("'render'", 1851), ("'style'", 1068), ("'dof'", 961), ("'field'", 747), ("'cute furry monster in Pixar with star, colorful, volumetric lighting, 4k, photorealistic'", 736), ("'8K'", 689), ("'realistic'", 689), ("'blur'", 672), ("'8k'", 648), ("'particles'", 492), ("'art'", 463), ("'clay'", 453)]
LABEL_DETAILS ratio rows 34993 unique 193 examples [("'16:9'", 12470), ("'9:16'", 4662), ("'2:3'", 2479), ("'3:4'", 1424), ("'4:5'", 1082), ("'2:1'", 841), ("'4:3'", 717), ("'3:2'", 707), ("'21:9'", 578), ("'9:20'", 530), ("'7:5'", 507), ("'3:1'", 475)]
LABEL_DETAILS parameter_only rows 13757 unique 27 examples [("'--uplight'", 9969), ("'--fast'", 932), ("'--test'", 740), ("'--wallpaper'", 609), ("'--hd'", 535), ("'--vibefast'", 328), ("'--vibe'", 85), ("'—hd'", 83), ("'--video'", 76), ("'—uplight'", 75), ("'—test'", 67), ("'--ll'", 54)]
LABEL_DETAILS number rows 12467 unique 270 examples [("'1920'", 2054), ("'1'", 1391), ("'1080'", 447), ("'80'", 443), ("'2'", 362), ("'350'", 351), ("'600'", 309), ("'5'", 228), ("'88'", 227), ("'90'", 225), ("'2000'", 208), ("'0.5'", 192)]
LABEL_DETAILS empty rows 1597 unique 1 examples [("''", 1597)]
DUPS all rows 246381 unique 65398 extra 180983 duplicate_group_rows 208436 duplicate_groups 27453
SPLIT all train rows 221743 unique 61505 in_train_rows - in_train_unique -
SPLIT all validation rows 12318 unique 7013 in_train_rows 10365 in_train_unique 5092
SPLIT all test rows 12320 unique 7150 in_train_rows 10239 in_train_unique 5114
DUPS nonempty rows 244784 unique 65397 extra 179387 duplicate_group_rows 206839 duplicate_groups 27452
SPLIT nonempty train rows 220307 unique 61504 in_train_rows - in_train_unique -
SPLIT nonempty validation rows 12228 unique 7012 in_train_rows 10275 in_train_unique 5091
SPLIT nonempty test rows 12249 unique 7149 in_train_rows 10168 in_train_unique 5113
DUPS not_flagged rows 183567 unique 64907 extra 118660 duplicate_group_rows 145681 duplicate_groups 27021
SPLIT not_flagged train rows 165138 unique 61022 in_train_rows - in_train_unique -
SPLIT not_flagged validation rows 9154 unique 6773 in_train_rows 7208 in_train_unique 4857
SPLIT not_flagged test rows 9275 unique 6906 in_train_rows 7199 in_train_unique 4875
LABELS_BY_SPLIT
train Counter({'not_flagged': 165138, 'ratio': 31551, 'parameter_only': 12362, 'number': 11256, 'empty': 1436})
validation Counter({'not_flagged': 9154, 'ratio': 1740, 'parameter_only': 718, 'number': 616, 'empty': 90})
test Counter({'not_flagged': 9275, 'ratio': 1702, 'parameter_only': 677, 'number': 595, 'empty': 71})
FLAGGED_AND_DUPLICATED_ROW_COUNT 0
FLAGGED_DUP_GROUP_ROWS 61158
UNFLAGGED_SHORT 1 52970
UNFLAGGED_SHORT 2 60535
UNFLAGGED_SHORT 3 64810
UNFLAGGED_SHORT 5 73889
UNFLAGGED_SINGLE_TOP [('render', 1851), ('style', 1068), ('dof', 961), ('field', 747), ('realistic', 689), ('blur', 672), ('particles', 492), ('art', 463), ('clay', 453), ('nouveau', 444), ('detailed', 412), ('light', 406), ('artstation', 391), ('text', 388), ('detail', 386), ('lighting', 348), ('photograph', 329), ('photography', 324), ('cinematic', 316), ('people', 299), ('engine', 298), ('design', 286), ('painting', 285), ('AlAkroka', 280), ('symmetrical', 246)]
```

**Tool: bash — Verify cleaning and overlap percentages**

Command:

```bash
python3 - <<'PY'
for name,a,b in [('empty',1597,246381),('flags',61217,246381),('empty_plus_flags',62814,246381),('dupextra',180983,246381),('duprows',208436,246381),('short',52970,183567),('valid',7208,9154),('test',7199,9275),('validall',10365,12318),('testall',10239,12320),('flagdups',61158,61217)]: print(name, round(100*a/b,2))
PY
```

Exit code: 0

Recorded output:

```text
empty 0.65
flags 24.85
empty_plus_flags 25.49
dupextra 73.46
duprows 84.6
short 28.86
valid 78.74
test 77.62
validall 84.15
testall 83.11
flagdups 99.9
```

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


## Exchange 3

**Request time:** 2026-11-08T12:23:51.134000-07:00

### Prompt

```text
Excluding rows that are not real prompts and removing duplicates, describe what a typical prompt looks like: its length in words, how often Midjourney parameters such as --ar, --no, --w/--h, --stop and --seed are used, and the most common aspect ratios.
```

### Response and recorded tool activity

I’ll apply the same non-prompt rule as before, deduplicate exact text, and count parameters and ratios per remaining distinct row.

**Tool: bash — Measure deduplicated prompt lengths, parameter use and aspect-ratio distributions**

Command:

```bash
python3 - <<'PY'
import csv,re,collections,statistics
p='midjourney_prompts_all.csv'
with open(p, encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
ratio_only=re.compile(r'\s*\d+\s*:\s*\d+\s*')
number_only=re.compile(r'\s*\d+(?:\.\d+)?\s*')
parameter_only=re.compile(r'\s*(?:(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)(?:\s+(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)*\s*',re.I)
url_only=re.compile(r'\s*https?://\S+\s*',re.I)
def keep(t):return bool(t.strip()) and not any(p.fullmatch(t) for p in (ratio_only,number_only,parameter_only,url_only))
ts=list(dict.fromkeys(r['text'] for r in rows if keep(r['text'])))
print('N',len(ts))
length=[len(t.split()) for t in ts]; sl=sorted(length)
print('WHITESPACE_LEN mean',statistics.mean(length),'median',statistics.median(length),'p10',sl[int(.1*(len(sl)-1))],'p25',sl[int(.25*(len(sl)-1))],'p75',sl[int(.75*(len(sl)-1))],'p90',sl[int(.9*(len(sl)-1))],'max',sl[-1])
for name,lo,hi in [('1',1,1),('2-5',2,5),('6-10',6,10),('11-20',11,20),('21-50',21,50),('51+',51,99999)]:
 n=sum(lo<=v<=hi for v in length); print('LENGTH_BIN',name,n,round(100*n/len(ts),2))
param_re=re.compile(r'(?<!\S)(?:--|[—–])([a-z][a-z0-9-]*)',re.I)
params=collections.Counter(); combined=collections.Counter()
for t in ts:
 ps={v.lower() for v in param_re.findall(t)}; params.update(ps)
 if ps:combined['any']+=1
 if {'w','h'}<=ps: combined['both_w_h']+=1
 if {'w','h'}&ps:combined['w_or_h']+=1
 if {'ar','aspect'}&ps:combined['ar_or_aspect']+=1
print('PARAMS',params.most_common(30));print('COMBINED',combined)
ratio_re=re.compile(r'(?<!\S)(?:--|[—–])(?:ar|aspect)\s+(\d+)\s*:\s*(\d+)',re.I)
ratio_counts=collections.Counter(); n_ratio=0; invalid=0; multi=0; raw_count=0; orientations=collections.Counter(); malformed=[]
for t in ts:
 matches=ratio_re.findall(t); valid=[(int(a),int(b)) for a,b in matches if int(a)>0 and int(b)>0]
 invalid+=len(matches)-len(valid)
 if valid:
  n_ratio+=1;raw_count+=len(valid)
  if len(valid)>1: multi+=1
  a,b=valid[0]; ratio_counts[f'{a}:{b}']+=1
  orientations['landscape' if a>b else 'portrait' if a<b else 'square']+=1
 elif re.search(r'(?<!\S)(?:--|[—–])(?:ar|aspect)\b',t,re.I):
  if len(malformed)<8:malformed.append(t[:240])
print('RATIO_VALID_ROWS',n_ratio,'MATCHES',raw_count,'ROWS_MULTIPLE',multi,'INVALID',invalid,'ORIENTATION',orientations)
print('RATIOS_FIRST',ratio_counts.most_common(20)); print('EXAMPLES_NO_RECOGNIZED_RATIO',malformed)
# Compare a restricted set: at least six word-like tokens, using the earlier method.
words=re.compile(r"[a-z]+(?:['’][a-z]+)?|\d+",re.I)
long=[t for t in ts if len(words.findall(t))>=6]
print('LONG_SET',len(long),'median_whitespace',statistics.median(len(t.split()) for t in long))
for name in ['ar','aspect','no','w','h','stop','seed']:
 n=sum(name in {v.lower() for v in param_re.findall(t)} for t in long);print('LONG_PARAM',name,n,round(100*n/len(long),2))
PY
```

Exit code: 0

Recorded output:

```text
N 64907
WHITESPACE_LEN mean 15.92883664319719 median 12 p10 2 p25 6 p75 21 p90 34 max 353
LENGTH_BIN 1 5127 7.9
LENGTH_BIN 2-5 9465 14.58
LENGTH_BIN 6-10 14180 21.85
LENGTH_BIN 11-20 18890 29.1
LENGTH_BIN 21-50 15382 23.7
LENGTH_BIN 51+ 1863 2.87
PARAMS [('ar', 17946), ('h', 3402), ('w', 3389), ('uplight', 3108), ('aspect', 2716), ('no', 2343), ('wallpaper', 756), ('stop', 738), ('hd', 668), ('test', 663), ('iw', 201), ('seed', 166), ('fast', 150), ('vibe', 117), ('style', 95), ('lp', 88), ('video', 79), ('ll', 78), ('ml', 47), ('vertical', 35), ('mp', 33), ('zineq', 29), ('greg', 14), ('vibefast', 14), ('land', 8), ('a2', 7), ('w2400', 6), ('h1200', 6), ('sameseed', 6), ('w750', 6)]
COMBINED Counter({'any': 27371, 'ar_or_aspect': 20662, 'w_or_h': 3848, 'both_w_h': 2943})
RATIO_VALID_ROWS 20662 MATCHES 20682 ROWS_MULTIPLE 19 INVALID 0 ORIENTATION Counter({'landscape': 11206, 'portrait': 9339, 'square': 117})
RATIOS_FIRST [('16:9', 6789), ('9:16', 2475), ('2:3', 1508), ('4:5', 819), ('16:8', 693), ('3:4', 602), ('11:17', 539), ('3:2', 471), ('2:1', 436), ('4:3', 388), ('7:5', 387), ('21:9', 341), ('1:2', 242), ('5:7', 220), ('4:6', 208), ('3:1', 202), ('8:13', 195), ('9:20', 176), ('9:21', 169), ('9:19', 159)]
EXAMPLES_NO_RECOGNIZED_RATIO []
LONG_SET 51451 median_whitespace 15
LONG_PARAM ar 17807 34.61
LONG_PARAM aspect 2681 5.21
LONG_PARAM no 2324 4.52
LONG_PARAM w 3367 6.54
LONG_PARAM h 3387 6.58
LONG_PARAM stop 734 1.43
LONG_PARAM seed 159 0.31
```

**Tool: bash — Verify handling of malformed and missing aspect-ratio values**

Command:

```bash
python3 - <<'PY'
import csv,re,collections
with open('midjourney_prompts_all.csv',encoding='utf-8-sig',newline='') as f: rows=csv.DictReader(f); ts=list(dict.fromkeys(r['text'] for r in rows))
prefix=re.compile(r'(?<!\S)(?:--|[—–])(?:ar|aspect)\b',re.I)
value=re.compile(r'(?<!\S)(?:--|[—–])(?:ar|aspect)\s+(\d+)\s*:\s*(\d+)',re.I)
both=[t for t in ts if prefix.search(t) and value.search(t)]; missing=[t for t in ts if prefix.search(t) and not value.search(t)]; print('prefix+value',len(both),'prefix without ratio',len(missing),'examples',list(map(repr,missing[:15])))
PY
```

Exit code: 0

Recorded output:

```text
prefix+value 20662 prefix without ratio 0 examples []
```

**Tool: bash — Calculate parameter and aspect-ratio percentages**

Command:

```bash
python3 - <<'PY'
n=64907;r=20662
for k,v in [('any',27371),('ar',17946),('aspect',2716),('ar_or_aspect',20662),('no',2343),('w',3389),('h',3402),('w_or_h',3848),('w_and_h',2943),('stop',738),('seed',166)]:print(k, v, f'{100*v/n:.2f}%')
for k,v in [('16:9',6789),('9:16',2475),('2:3',1508),('4:5',819),('16:8',693),('3:4',602),('11:17',539),('3:2',471),('landscape',11206),('portrait',9339),('square',117)]:print(k,v,f'{100*v/r:.2f}%',f'of all {100*v/n:.2f}%')
PY
```

Exit code: 0

Recorded output:

```text
any 27371 42.17%
ar 17946 27.65%
aspect 2716 4.18%
ar_or_aspect 20662 31.83%
no 2343 3.61%
w 3389 5.22%
h 3402 5.24%
w_or_h 3848 5.93%
w_and_h 2943 4.53%
stop 738 1.14%
seed 166 0.26%
16:9 6789 32.86% of all 10.46%
9:16 2475 11.98% of all 3.81%
2:3 1508 7.30% of all 2.32%
4:5 819 3.96% of all 1.26%
16:8 693 3.35% of all 1.07%
3:4 602 2.91% of all 0.93%
11:17 539 2.61% of all 0.83%
3:2 471 2.28% of all 0.73%
landscape 11206 54.23% of all 17.26%
portrait 9339 45.20% of all 14.39%
square 117 0.57% of all 0.18%
```

**Tool: bash — Measure descriptive terms within the same cleaned, unique population**

Command:

```bash
python3 - <<'PY'
import csv,re,collections
with open('midjourney_prompts_all.csv',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
pats=[re.compile(r'\s*\d+\s*:\s*\d+\s*'),re.compile(r'\s*\d+(?:\.\d+)?\s*'),re.compile(r'\s*(?:(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)(?:\s+(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)*\s*',re.I),re.compile(r'\s*https?://\S+\s*',re.I)]
ts=set(r['text'] for r in rows if r['text'].strip() and not any(p.fullmatch(r['text']) for p in pats))
for phrase in ['cinematic','style of','octane render','highly detailed','unreal engine','portrait','photorealistic','lighting']:
 rx=re.compile(r'\b'+re.escape(phrase).replace('\\ ',r'\s+')+r'\b',re.I);c=sum(bool(rx.search(t)) for t in ts);print(phrase,c,round(100*c/len(ts),2))
PY
```

Exit code: 0

Recorded output:

```text
cinematic 6240 9.61
style of 4530 6.98
octane render 4452 6.86
highly detailed 2723 4.2
unreal engine 2338 3.6
portrait 3190 4.91
photorealistic 1953 3.01
lighting 4341 6.69
```

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


## Exchange 4

**Request time:** 2026-11-08T12:25:15.519000-07:00

### Prompt

```text
What share of prompts reference a named artist or "in the style of" someone? Which artists are named most often? What share use generic quality phrases such as "trending on artstation", "8k" or "octane render"? State the rule you used to detect each.
```

### Response and recorded tool activity

I’ll use the same cleaned, exact-deduplicated rows as the previous answer. Artist references need a transparent detection rule, so I’ll distinguish explicit phrase matches from names found using a defined list.

**Tool: bash — Identify frequently occurring candidate artist names and reference constructions**

Command:

```bash
python3 - <<'PY'
import csv,re,collections
with open('midjourney_prompts_all.csv',encoding='utf-8-sig',newline='') as f: rows=csv.DictReader(f); texts=list(dict.fromkeys(r['text'] for r in rows))
pats=[re.compile(r'\s*\d+\s*:\s*\d+\s*'),re.compile(r'\s*\d+(?:\.\d+)?\s*'),re.compile(r'\s*(?:(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)(?:\s+(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)*\s*',re.I),re.compile(r'\s*https?://\S+\s*',re.I)]
ts=[t for t in texts if t.strip() and not any(p.fullmatch(t) for p in pats)]
for pat in [r'\b(?:in the style of|style of|inspired by|art by|painting by|illustration by|drawn by|painted by)\s+([^,;:.()\n]{2,100})',r'\bby\s+([^,;:.()\n]{2,100})']:
 c=collections.Counter(); examples={}
 for t in ts:
  for m in re.finditer(pat,t,re.I):
   x=m.group(1).lower().strip(); x=re.split(r'\s+(?:and|with|in|by|on|of|--|—)\b',x)[0]; x=' '.join(re.findall(r"[\w'’éœ.-]+",x,flags=re.UNICODE)[:3]);
   if x: c[x]+=1; examples.setdefault(x,m.group(1)[:80])
 print('\nPAT',pat,'top:')
 for x,n in c.most_common(90):print(n,repr(x),'EX',repr(examples[x]))
PY
```

Exit code: 0

Recorded output:

```text
Output too large to read at once (8.1 KB). Saved to: /tmp/1794165929715-copilot-tool-output-7333-fccec5ef-b6c2-4953-a14e-a68d28db994e.txt
Consider using tools like rg (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):

PAT \b(?:in the style of|style of|inspired by|art by|painting by|illustration by|drawn by|painted by)\s+([^,;:.()\n]{2,100}) top:
208 'craig mullins' EX 'Craig Mullins and remy cogghe —ar 9'
124 'stefan gesell' EX 'stefan gesell and caravaggio --aspect 11'
102 'jean-michel basquiat' EX 'Jean-Michel Basquiat'
97 'filip hodas' EX 'Filip Hodas'
84 'yousuf karsh' EX 'Yousuf Karsh'
61 'james jean' EX 'James Jean'
60 'floria sigismondi' EX 'floria sigismondi and matt mahurin and robert mapplethorpe c
```

The referenced offloaded output is no longer available.

**Tool: view — Read tool output**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Tool: view — Read tool output**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Tool: bash — Quantify artist-name and style-reference proxies alongside quality-phrase matches**

Command:

```bash
python3 - <<'PY'
import csv,re,collections
with open('midjourney_prompts_all.csv',encoding='utf-8-sig',newline='') as f: rows=csv.DictReader(f); texts=list(dict.fromkeys(r['text'] for r in rows))
pats=[re.compile(r'\s*\d+\s*:\s*\d+\s*'),re.compile(r'\s*\d+(?:\.\d+)?\s*'),re.compile(r'\s*(?:(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)(?:\s+(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)*\s*',re.I),re.compile(r'\s*https?://\S+\s*',re.I)]
ts=[t for t in texts if t.strip() and not any(p.fullmatch(t) for p in pats)]; N=len(ts)
artists={
'Craig Mullins':['craig mullins'], 'Peter Mohrbacher':['peter mohrbacher'], 'Tsutomu Nihei':['tsutomu nihei'], 'Floria Sigismondi':['floria sigismondi'], 'Robert Mapplethorpe':['robert mapplethorpe'], 'Ashley Wood':['ashley wood'], 'Hajime Sorayama':['hajime sorayama'], 'Sarah Morris':['sarah morris'], 'Annie Leibovitz':['annie leibovitz'], 'WLOP':['wlop'], 'Hokusai':['hokusai'], 'Hayao Miyazaki':['hayao miyazaki'], 'Ansel Adams':['ansel adams'], 'Joel Meyerowitz':['joel meyerowitz'], 'Karel Thole':['karel thole'], 'Alphonse Mucha':['alphonse mucha','alfons mucha','mucha'], 'James Jean':['james jean'], 'Renato Muccillo':['renato muccillo'], 'Artgerm':['artgerm'], 'Thomas Kinkade':['thomas kinkade','thomas kindkade'], 'Katsuhiro Otomo':['katsuhiro otomo'], 'Jean-Honoré Fragonard':['jean-honoré fragonard','jean-honore fragonard'], 'Harumi Hironaka':['harumi hironaka'], 'Charlie Bowater':['charlie bowater'], 'Mœbius':['mœbius','moebius','moebius','jean giraud'], 'Greg Rutkowski':['greg rutkowski'], 'Kilian Eng':['kilian eng'], 'Marc Simonetti':['marc simonetti'], 'Gustave Doré':['gustave dore','gustave doré'], 'Beeple':['beeple'], 'Tom Bagshaw':['tom bagshaw'], 'Andrei Riabovitchev':['andrei riabovitchev'], 'Ross Tran':['ross tran'], 'Yoshitaka Amano':['yoshitaka amano'], 'Yoji Shinkawa':['yoji shinkawa'], 'Tim Burton':['tim burton'], 'Tim Walker':['tim walker'], 'Wes Anderson':['wes anderson'], 'Norman Rockwell':['norman rockwell'], 'Makoto Shinkai':['makoto shinkai'], 'Emil Melmoth':['emil melmoth'], 'James Gurney':['james gurney'], 'Syd Mead':['syd mead'], 'Filip Hodas':['filip hodas'], 'Stefan Gesell':['stefan gesell'], 'Jean-Michel Basquiat':['jean-michel basquiat','basquiat'], 'Yousuf Karsh':['yousuf karsh'], 'H. R. Giger':['hr giger','h.r. giger','giger'], 'Zdzisław Beksiński':['zdzisław beksiński','zdzislaw beksinski','beksinski','beksinkski'], 'Vincent van Gogh':['vincent van gogh','van gogh']}
def literal(s):return r'(?<!\w)'+r'\s+'.join(re.escape(x) for x in s.split())+r'(?!\w)'
ars={k:re.compile('|'.join(literal(s) for s in aliases),re.I) for k,aliases in artists.items()}
counts=collections.Counter(); matched=set()
for i,t in enumerate(ts):
 for name,rx in ars.items():
  if rx.search(t): counts[name]+=1;matched.add(i)
phrase=re.compile(r'\bin\s+the\s+style\s+of\b',re.I)
style={i for i,t in enumerate(ts) if phrase.search(t)}
print('N',N,'ARTIST_LIST_LEN',len(artists),'ARTISTS_MATCH',len(matched),'PCT',round(100*len(matched)/N,2),'STYLE',len(style),round(100*len(style)/N,2),'UNION',len(style|matched),round(100*len(style|matched)/N,2),'INTERSECTION',len(style&matched))
print('ARTIST_COUNTS',counts.most_common())
qp={'trending on artstation':r'(?<!\w)trending\s+on\s+artstation(?!\w)','8k':r'(?<!\w)8k(?!\w)','octane render':r'(?<!\w)octane\s+render(?!\w)','highly detailed':r'(?<!\w)highly\s+detailed(?!\w)','4k':r'(?<!\w)4k(?!\w)','unreal engine':r'(?<!\w)unreal\s+engine(?!\w)'}
sets={k:{i for i,t in enumerate(ts) if re.search(p,t,re.I)} for k,p in qp.items()}
for k,v in sets.items():print('QUALITY',k,len(v),round(100*len(v)/N,2))
for group in [('trending on artstation','8k','octane render'),tuple(qp)]:
 u=set().union(*(sets[k] for k in group));print('QUALITY_UNION',group,len(u),round(100*len(u)/N,2))
print('STYLE_EXAMPLES_WITHOUT_ARTIST_LIST')
for i in list(sorted(style-matched))[:12]:
 t=ts[i];m=phrase.search(t);print(repr(t[max(0,m.start()-20):m.start()+110]))
PY
```

Exit code: 0

Recorded output:

```text
N 64907 ARTIST_LIST_LEN 50 ARTISTS_MATCH 8786 PCT 13.54 STYLE 3689 5.68 UNION 11040 17.01 INTERSECTION 1435
ARTIST_COUNTS [('Craig Mullins', 1283), ('Peter Mohrbacher', 963), ('Alphonse Mucha', 817), ('H. R. Giger', 678), ('Mœbius', 573), ('James Jean', 516), ('Artgerm', 515), ('James Gurney', 423), ('Ashley Wood', 401), ('Zdzisław Beksiński', 392), ('Ross Tran', 386), ('Marc Simonetti', 344), ('WLOP', 309), ('Greg Rutkowski', 301), ('Ansel Adams', 296), ('Hokusai', 289), ('Charlie Bowater', 267), ('Emil Melmoth', 265), ('Yoji Shinkawa', 225), ('Tsutomu Nihei', 221), ('Wes Anderson', 206), ('Norman Rockwell', 204), ('Thomas Kinkade', 200), ('Hajime Sorayama', 199), ('Tom Bagshaw', 196), ('Sarah Morris', 188), ('Annie Leibovitz', 173), ('Stefan Gesell', 171), ('Jean-Michel Basquiat', 157), ('Gustave Doré', 154), ('Katsuhiro Otomo', 145), ('Syd Mead', 144), ('Makoto Shinkai', 142), ('Yoshitaka Amano', 141), ('Filip Hodas', 132), ('Karel Thole', 125), ('Hayao Miyazaki', 120), ('Vincent van Gogh', 117), ('Joel Meyerowitz', 117), ('Beeple', 115), ('Tim Burton', 112), ('Renato Muccillo', 99), ('Robert Mapplethorpe', 90), ('Tim Walker', 84), ('Yousuf Karsh', 84), ('Andrei Riabovitchev', 83), ('Floria Sigismondi', 75), ('Jean-Honoré Fragonard', 73), ('Kilian Eng', 66), ('Harumi Hironaka', 65)]
QUALITY trending on artstation 2130 3.28
QUALITY 8k 5915 9.11
QUALITY octane render 4452 6.86
QUALITY highly detailed 2723 4.2
QUALITY 4k 3162 4.87
QUALITY unreal engine 2338 3.6
QUALITY_UNION ('trending on artstation', '8k', 'octane render') 9948 15.33
QUALITY_UNION ('trending on artstation', '8k', 'octane render', 'highly detailed', '4k', 'unreal engine') 14119 21.75
STYLE_EXAMPLES_WITHOUT_ARTIST_LIST
"r smashing a guitar in the style of a 1970's illustration"
'ripping wet, storm, in the style of Blade Runner, neon lights'
'galaxies collide :: in the style of amano --w 128 --h 256'
' from despicable me in the style of Junji Ito'
'g down at a city :: in the style of ffix --w 256 --h 160'
'with fluffy animals in the style of ghibli and ‘wiebke rauers’ --ar 9:16'
'hes National Park:: in the style of a Native American woodcut::'
'cars, street signs, in the style of Gregory crewdson, 8k, trending on artstation --test'
'ng you to shipwreck in the style of leyendecker'
'ired by art nouveau in the style of alex grey oil painted --ar 7:11 --uplight'
'et, matte painting, in the style of Vermeer, highly detailed, hyperrealistic, --no dof, --ar 9:16'
' lighting the mist, in the style of William Turner --ar 16:8'
```

**Tool: bash — Verify leading artist-name percentages**

Command:

```bash
python3 - <<'PY'
for name, n in [('Craig Mullins',1283),('Peter Mohrbacher',963),('Alphonse Mucha',817),('H. R. Giger',678),('Mœbius',573),('James Jean',516),('Artgerm',515),('James Gurney',423),('Ashley Wood',401),('Zdzisław Beksiński',392)]: print(name, f'{100*n/64907:.2f}%')
PY
```

Exit code: 0

Recorded output:

```text
Craig Mullins 1.98%
Peter Mohrbacher 1.48%
Alphonse Mucha 1.26%
H. R. Giger 1.04%
Mœbius 0.88%
James Jean 0.79%
Artgerm 0.79%
James Gurney 0.65%
Ashley Wood 0.62%
Zdzisław Beksiński 0.60%
```

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


## Exchange 5

**Request time:** 2026-11-08T12:27:00.700000-07:00

### Prompt

```text
Identify the main themes or topics in the prompts using a topic model. Report the topics with their top words and the share of prompts in each. How stable are these topics if the analysis is re-run?
```

### Response and recorded tool activity

I’ll fit a topic model to the same cleaned, deduplicated texts, then rerun it with different random seeds and compare the resulting topics rather than assuming they are stable.

**Tool: bash — Check availability of topic-modeling libraries**

Command:

```bash
python3 - <<'PY'
import sys, importlib.util
print('python',sys.version)
for name in ['numpy','scipy','sklearn','pandas']:
 print(name, bool(importlib.util.find_spec(name)))
PY
```

Exit code: 0

Recorded output:

```text
python 3.8.10 (default, Mar 18 2025, 20:04:55) 
[GCC 9.4.0]
numpy True
scipy True
sklearn True
pandas True
```

**Tool: apply_patch — Edit [](file:///home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/topic_analysis.py)**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Recorded file edit:** `/home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/topic_analysis.py`. The export records the edit but not the complete patch; available script contents are included in the appendix.

**Tool: bash — Fit and compare three randomly initialized topic models**

Command:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 /home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/topic_analysis.py
```

Exit code: 0

Recorded output:

```text
DATA 64907 MODELED 61246 NO_FEATURES 3661 VOCAB 4430
FIT 0 iterations 132 reconstruction_error 241.15915667312433 warnings []
TOPIC 0 0 count 8375 words render,realistic,octane,hyper,unreal,engine,ultra,photo,high,artstation,post,alien
TOPIC 0 1 count 5693 words painting,oil,matte,abstract,beautiful,battle,hyperrealistic,cgsociety,large,mecha,realistic,space
TOPIC 0 2 count 5372 words detailed,highly,intricate,hyper,cgsociety,alien,insanely,ornate,sci,artstation,blue,golden
TOPIC 0 3 count 5179 words art,concept,vector,fantasy,digital,psychedelic,circa,pulp,symmetrical,magazine,flat,centered
TOPIC 0 4 count 6782 words portrait,beautiful,artstation,character,face,girl,trending,wood,woman,ashley,hair,body
TOPIC 0 5 count 1304 words clay,shot,length,cute,race,sculpture,man,king,animation,dinosaur,photorealistic,wide
TOPIC 0 6 count 7862 words black,white,photo,background,red,ink,paper,photograph,illustration,card,old,wearing
TOPIC 0 7 count 577 words artwork,van,john,peter,mike,robert,david,shinkawa,yoji,james,paul,hans
TOPIC 0 8 count 7230 words style,anime,ghibli,pixar,poster,design,mullins,basquiat,jean,giger,craig,game
TOPIC 0 9 count 12872 words cinematic,lighting,dark,light,epic,city,high,dramatic,shot,wide,photorealistic,angle
FIT 1 iterations 197 reconstruction_error 241.05313409102638 warnings []
TOPIC 1 0 count 5818 words realistic,hyper,photo,ultra,old,realism,view,detailed,photograph,super,epic,grotty
TOPIC 1 1 count 5574 words art,concept,vector,fantasy,digital,psychedelic,circa,pulp,symmetrical,magazine,flat,centered
TOPIC 1 2 count 7330 words portrait,beautiful,artstation,character,face,girl,trending,wood,woman,ashley,hair,body
TOPIC 1 3 count 9396 words black,white,background,red,photo,ink,paper,illustration,photograph,card,wearing,tarot
TOPIC 1 4 count 580 words artwork,van,john,peter,mike,robert,david,shinkawa,yoji,james,paul,hans
TOPIC 1 5 count 4904 words painting,oil,matte,abstract,beautiful,battle,hyperrealistic,cgsociety,large,mecha,space,trending
TOPIC 1 6 count 13200 words cinematic,lighting,dark,light,city,epic,shot,dramatic,high,wide,photorealistic,angle
TOPIC 1 7 count 5735 words style,anime,ghibli,pixar,poster,design,mullins,basquiat,jean,giger,craig,game
TOPIC 1 8 count 4041 words render,octane,unreal,engine,artstation,high,alien,photorealistic,blue,post,yellow,cyberpunk
TOPIC 1 9 count 4668 words detailed,highly,intricate,cgsociety,alien,artstation,ornate,sci,insanely,blue,golden,yellow
FIT 2 iterations 261 reconstruction_error 241.08635137782423 warnings []
TOPIC 2 0 count 8160 words render,octane,unreal,engine,high,photorealistic,alien,blue,cyberpunk,yellow,space,ultra
TOPIC 2 1 count 6356 words painting,oil,matte,beautiful,abstract,space,battle,hyperrealistic,cgsociety,large,mecha,landscape
TOPIC 2 2 count 5052 words art,concept,vector,fantasy,digital,circa,psychedelic,pulp,symmetrical,magazine,flat,miyazaki
TOPIC 2 3 count 583 words artwork,van,john,peter,mike,robert,david,shinkawa,yoji,paul,james,hans
TOPIC 2 4 count 4538 words realistic,hyper,photo,ultra,old,realism,epic,view,detailed,photography,high,super
TOPIC 2 5 count 9667 words black,white,background,red,ink,photo,paper,illustration,dark,card,photograph,tarot
TOPIC 2 6 count 5975 words portrait,face,beautiful,character,girl,woman,hair,man,symmetrical,body,wood,ashley
TOPIC 2 7 count 8867 words detailed,cinematic,highly,lighting,intricate,dark,dramatic,shot,epic,cgsociety,wide,insanely
TOPIC 2 8 count 7526 words style,anime,ghibli,poster,city,pixar,studio,basquiat,jean,mullins,giger,japanese
TOPIC 2 9 count 4522 words artstation,trending,design,craig,beautiful,mullins,concept,game,mucha,high,girl,wood
STABILITY 1 cosine_mean 0.8817150391254357 cosine_min 0.005357467326112247 jaccard10_mean 0.8246753246753247 jaccard10_min 0.0 agreement 0.8120367044378408
MATCH 1 0 8 cos 0.819 jaccard 0.429 ref_share 0.1367 other_share 0.066
MATCH 1 1 5 cos 0.999 jaccard 1.0 ref_share 0.093 other_share 0.0801
MATCH 1 2 9 cos 0.998 jaccard 0.818 ref_share 0.0877 other_share 0.0762
MATCH 1 3 1 cos 1.0 jaccard 1.0 ref_share 0.0846 other_share 0.091
MATCH 1 4 2 cos 1.0 jaccard 1.0 ref_share 0.1107 other_share 0.1197
MATCH 1 5 0 cos 0.005 jaccard 0.0 ref_share 0.0213 other_share 0.095
MATCH 1 6 3 cos 0.999 jaccard 1.0 ref_share 0.1284 other_share 0.1534
MATCH 1 7 4 cos 1.0 jaccard 1.0 ref_share 0.0094 other_share 0.0095
MATCH 1 8 7 cos 1.0 jaccard 1.0 ref_share 0.118 other_share 0.0936
MATCH 1 9 6 cos 0.997 jaccard 1.0 ref_share 0.2102 other_share 0.2155
STABILITY 2 cosine_mean 0.7588369421272447 cosine_min 0.006620941951629823 jaccard10_mean 0.5185748462064251 jaccard10_min 0.0 agreement 0.6053783104202723
MATCH 2 0 0 cos 0.813 jaccard 0.333 ref_share 0.1367 other_share 0.1332
MATCH 2 1 1 cos 0.997 jaccard 0.818 ref_share 0.093 other_share 0.1038
MATCH 2 2 7 cos 0.766 jaccard 0.25 ref_share 0.0877 other_share 0.1448
MATCH 2 3 2 cos 0.996 jaccard 1.0 ref_share 0.0846 other_share 0.0825
MATCH 2 4 6 cos 0.891 jaccard 0.429 ref_share 0.1107 other_share 0.0976
MATCH 2 5 4 cos 0.007 jaccard 0.0 ref_share 0.0213 other_share 0.0741
MATCH 2 6 5 cos 0.994 jaccard 0.818 ref_share 0.1284 other_share 0.1578
MATCH 2 7 3 cos 1.0 jaccard 0.818 ref_share 0.0094 other_share 0.0095
MATCH 2 8 8 cos 0.996 jaccard 0.667 ref_share 0.118 other_share 0.1229
MATCH 2 9 9 cos 0.129 jaccard 0.053 ref_share 0.2102 other_share 0.0738
```

**Tool: bash — Verify baseline topic shares and unmodelled-text percentage**

Command:

```bash
python3 - <<'PY'
n=61246
for k,v in [('render',8375),('painting',5693),('detailed',5372),('art',5179),('portrait',6782),('clay',1304),('blackwhite',7862),('artwork',577),('style',7230),('cinematic',12872)]:print(k, f'{100*v/n:.2f}%')
print('excluded', f'{100*3661/64907:.2f}%')
PY
```

Exit code: 0

Recorded output:

```text
render 13.67%
painting 9.30%
detailed 8.77%
art 8.46%
portrait 11.07%
clay 2.13%
blackwhite 12.84%
artwork 0.94%
style 11.80%
cinematic 21.02%
excluded 5.64%
```

**Tool: add_artifact_or_reference — Add artifact "Reproducible topic-model analysis"**

The export does not contain a complete input/output transcript for this nonterminal tool call.

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


## Exchange 6

**Request time:** 2026-11-08T12:28:53.568000-07:00

### Prompt

```text
Test two hypotheses and report the test, test statistic, p-value and an effect size for each: (H1) prompts that use at least one parameter are longer than prompts that use none; (H2) prompts that name an artist are more likely to use a quality phrase.
```

### Response and recorded tool activity

I’ll test these on the same cleaned, deduplicated rows and use the previously defined artist and quality-phrase rules. For length, I’ll also check whether the result persists after removing parameter tokens.

**Tool: apply_patch — Edit [](file:///home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/hypothesis_tests.py)**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Recorded file edit:** `/home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/hypothesis_tests.py`. The export records the edit but not the complete patch; available script contents are included in the appendix.

**Tool: bash — Run length and artist–quality association tests**

Command:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 /home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/hypothesis_tests.py
```

Exit code: 0

Recorded output:

```text
DATA 64907 PARAMS 27371 ARTIST 8786 QUALITY 14119
H1_FULL n1 27371 n0 37536 mean1 23.111249132293302 mean0 10.691469522591646 median1 19.0 median0 8.0 U 820121638.0 p 0.0 log10p -3676.7812918563804 prob_superiority 0.7982512647953199 rank_biserial 0.5965025295906399 mean_difference 12.419779609701656
H1_WITHOUT_OPTIONS n1 27371 n0 37536 mean1 20.611742355047312 mean0 10.691469522591646 median1 17.0 median0 8.0 U 763579147.5 p 0.0 log10p -2446.3580206121983 prob_superiority 0.7432166059532832 rank_biserial 0.4864332119065664 mean_difference 9.920272832455666
H2 table [[3502, 5284], [10617, 45504]] chi2 1957.1775201587254 df 1 p 0.0 log10p -426.73979521859593 odds_ratio 2.840541182827278 odds_ratio_ci95 [2.708371102339983, 2.9791612398930876] artist_rate 0.3985886637832916 other_rate 0.18918052066071525 risk_difference 0.20940814312257636 risk_ratio 2.106922332126034 expected [[1911.1888394163957, 6874.811160583604], [12207.811160583604, 43913.1888394164]]
```

**Tool: bash — Convert log p-values to scientific notation without floating-point underflow**

Command:

```bash
python3 - <<'PY'
import math
for logp in (-3676.7812918563804,-2446.3580206121983,-426.73979521859593):
 e=math.floor(logp);print(f'{10**(logp-e):.3f}e{e}')
PY
```

Exit code: 0

Recorded output:

```text
1.655e-3677
4.385e-2447
1.821e-427
```

**Tool: add_artifact_or_reference — Add artifact "Reproducible hypothesis tests"**

The export does not contain a complete input/output transcript for this nonterminal tool call.

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


## Exchange 7

**Request time:** 2026-11-08T12:30:46.097000-07:00

### Prompt

```text
Give me the complete code you ran for all of the above, in one block, so that I can reproduce your results.
```

### Response and recorded tool activity

The analysis used several separate commands and two scripts. I’ll consolidate them into one self-contained program and check that it reproduces the reported figures.

**Tool: apply_patch — Edit [](file:///home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py)**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Recorded file edit:** `/home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py`. The export records the edit but not the complete patch; available script contents are included in the appendix.

**Tool: bash — Verify the consolidated reproducibility script against the reported results**

Command:

```bash
python3 /home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py
```

Exit code: 0

Recorded output:

```text
Output too large to read at once (11.1 KB). Saved to: /tmp/1794166344455-copilot-tool-output-7333-7e7cc781-4fdb-4bd2-b147-7e843d8c59e2.txt
Consider using tools like rg (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
VERSIONS numpy 1.24.4 scipy 1.10.1 scikit-learn 1.3.2

DATA QUALITY
ROWS 246381 SPLITS Counter({'train': 221743, 'test': 12320, 'validation': 12318})
CATEGORIES Counter({'not_flagged': 183567, 'ratio': 34993, 'parameter_only': 13757, 'number': 12467, 'empty': 1597})
EXACT_UNIQUE 65398 DUPLICATE_EXTRA 180983 ROWS_IN_DUP_GROUPS 208436 DUPLICATE_GROUPS 27453
TOP_REPEATED [('16:9', 12470), ('--uplight', 9969), ('9:16', 4662), ('2:3', 2479), ('1920', 2054), ('render', 1851), ('', 1597), ('3:4', 1424)
```

The referenced offloaded output is no longer available.

**Tool: rg — Search for `^(MODELED|FIT |STABILITY|H1_|H2_|ARTISTS|QUALITY_|ASPECT_RATIOS|WHITESPACE_LE...`**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Tool: apply_patch — Edit [](file:///home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py)**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Recorded file edit:** `/home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py`. The export records the edit but not the complete patch; available script contents are included in the appendix.

**Tool: bash — Confirm consolidated script reproduces cleaning, descriptive, modeling and test results**

Command:

```bash
python3 /home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py | grep -E '^(ROWS|CATEGORIES|EXACT_UNIQUE|NOT_FLAGGED_ONE_WORDLIKE|SIX_WORDLIKE|DESCRIPTIVE|MODELED|STABILITY|H1_|H2_)'
```

Exit code: 0

Recorded output:

```text
ROWS 246381 SPLITS Counter({'train': 221743, 'test': 12320, 'validation': 12318})
CATEGORIES Counter({'not_flagged': 183567, 'ratio': 34993, 'parameter_only': 13757, 'number': 12467, 'empty': 1597})
EXACT_UNIQUE 65398 DUPLICATE_EXTRA 180983 ROWS_IN_DUP_GROUPS 208436 DUPLICATE_GROUPS 27453
NOT_FLAGGED_ONE_WORDLIKE 51872
SIX_WORDLIKE 51451 median_whitespace_length 15
DESCRIPTIVE clean {'cinematic': 6240, 'style of': 4530, 'octane render': 4452, 'portrait(s)': 3196, 'highly detailed': 2723, 'unreal engine': 2338, 'trending on artstation': 2130, 'photorealistic': 1953, 'Craig Mullins': 1283, 'Peter Mohrbacher': 963}
DESCRIPTIVE six_wordlike {'cinematic': 6205, 'style of': 4525, 'octane render': 4434, 'portrait(s)': 3096, 'highly detailed': 2715, 'unreal engine': 2333, 'trending on artstation': 2125, 'photorealistic': 1896, 'Craig Mullins': 1280, 'Peter Mohrbacher': 961}
MODELED 61246 NO_FEATURES 3661 VOCAB 4430
STABILITY 1 mean_cosine 0.8817150391254357 min_cosine 0.005357467326112247 mean_top10_jaccard 0.8246753246753247 min_top10_jaccard 0.0 assignment_agreement 0.8120367044378408
STABILITY 2 mean_cosine 0.7588369421272447 min_cosine 0.006620941951629823 mean_top10_jaccard 0.5185748462064251 min_top10_jaccard 0.0 assignment_agreement 0.6053783104202723
H1_FULL n 27371 37536 means 23.111249132293302 10.691469522591646 medians 19.0 8.0 U 820121638.0 log10_p -3676.7812918563804 probability_superiority 0.7982512647953199 rank_biserial 0.5965025295906399
H1_WITHOUT_OPTIONS n 27371 37536 means 20.611742355047312 10.691469522591646 medians 17.0 8.0 U 763579147.5 log10_p -2446.3580206121983 probability_superiority 0.7432166059532832 rank_biserial 0.4864332119065664
H2_TABLE [[3502, 5284], [10617, 45504]] chi2 1957.1775201587254 df 1 log10_p -426.73979521859593 odds_ratio 2.840541182827278 or_95ci [2.708371102339983, 2.9791612398930876] rates 0.3985886637832916 0.18918052066071525 risk_difference 0.20940814312257636 risk_ratio 2.106922332126034
```

**Tool: apply_patch — Edit [](file:///home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py)**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Recorded file edit:** `/home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py`. The export records the edit but not the complete patch; available script contents are included in the appendix.

**Tool: view — Read [](file:///home/elta/.copilot/session-state/8489d557-d5c2-4c6b-b76e-dcc81fa073c0/files/reproduce_all.py)**

The export does not contain a complete input/output transcript for this nonterminal tool call.

**Tool: add_artifact_or_reference — Add artifact "Complete reproducible analysis"**

The export does not contain a complete input/output transcript for this nonterminal tool call.

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


## Exchange 8

### Prompt

```text
Save artifacts to this directory as run-A-(filename)
```

The message also tagged `/home/elta/mj-ai-run-A/run-A.json`.

### Response

Saved and verified:

- [run-A-reproduce_all.py](/home/elta/mj-ai-run-A/run-A-reproduce_all.py)
- [run-A-topic_analysis.py](/home/elta/mj-ai-run-A/run-A-topic_analysis.py)
- [run-A-hypothesis_tests.py](/home/elta/mj-ai-run-A/run-A-hypothesis_tests.py)

The existing [run-A.json](/home/elta/mj-ai-run-A/run-A.json) was not changed.

## Exchange 9

### Prompt

```text
Save all responses to this directory as run-A.md
```

The message also tagged `/home/elta/mj-ai-run-A/run-A.json`.

### Response

Saved all prior responses, including the code and correction, to [run-A.md](/home/elta/mj-ai-run-A/run-A.md).

## Appendix: script contents

The topic and hypothesis scripts below are the saved copies used by the recorded commands. The consolidated script was edited multiple times: the copy below is the final saved version, not necessarily the exact intermediate version used in every earlier validation call. The analysis-code block in Exchange 7 is the full response as exported.

### run-A-topic_analysis.py

```python
import csv
import re
import warnings

import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics.pairwise import cosine_similarity


path = "/home/elta/mj-ai-run-A/midjourney_prompts_all.csv"
filters = [
    re.compile(r"\s*\d+\s*:\s*\d+\s*"),
    re.compile(r"\s*\d+(?:\.\d+)?\s*"),
    re.compile(
        r"\s*(?:(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)"
        r"(?:\s+(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)*\s*",
        re.I,
    ),
    re.compile(r"\s*https?://\S+\s*", re.I),
]
with open(path, encoding="utf-8-sig", newline="") as file:
    texts = list(dict.fromkeys(
        row["text"] for row in csv.DictReader(file)
        if row["text"].strip() and not any(p.fullmatch(row["text"]) for p in filters)
    ))

url = re.compile(r"https?://\S+", re.I)
parameter = re.compile(
    r"(?<!\S)(?:--|[—–])([a-z][a-z0-9-]*)"
    r"(?:\s+(?!(?:--|[—–]))(\S+))?",
    re.I,
)
value_options = {"ar", "aspect", "w", "h", "stop", "seed", "iw", "no", "style", "q", "quality", "s", "stylize", "v", "version", "chaos", "c"}


def clean(text):
    def remove_option(match):
        name, value = match.groups()
        return " " if value is None or name.lower() in value_options else " " + value

    return parameter.sub(remove_option, url.sub(" ", text))


vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    token_pattern=r"(?u)\b[a-zA-Z]{3,}\b",
    min_df=20,
    max_df=0.6,
    max_features=8000,
    sublinear_tf=True,
)
matrix = vectorizer.fit_transform(clean(t) for t in texts)
nonzero = np.asarray(matrix.getnnz(axis=1)).ravel() > 0
matrix = matrix[nonzero]
terms = vectorizer.get_feature_names_out()
print("DATA", len(texts), "MODELED", matrix.shape[0], "NO_FEATURES", int((~nonzero).sum()), "VOCAB", len(terms), flush=True)

models = []
for seed in (0, 1, 2):
    model = NMF(
        n_components=10,
        init="random",
        random_state=seed,
        max_iter=500,
        tol=1e-4,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        weights = model.fit_transform(matrix)
    assignment = weights.argmax(axis=1)
    print("FIT", seed, "iterations", model.n_iter_, "reconstruction_error", model.reconstruction_err_,
          "warnings", [str(w.message) for w in caught], flush=True)
    models.append((model.components_, assignment))
    for i, component in enumerate(model.components_):
        top = component.argsort()[-12:][::-1]
        print("TOPIC", seed, i, "count", int((assignment == i).sum()), "words", ",".join(terms[top]), flush=True)

reference, reference_assignment = models[0]
for seed, (components, assignment) in zip((1, 2), models[1:]):
    sim = cosine_similarity(reference, components)
    old, new = linear_sum_assignment(-sim)
    mapping = np.empty(10, dtype=int)
    mapping[new] = old
    aligned_assignment = mapping[assignment]
    similarities = sim[old, new]
    jaccards = []
    for i, j in zip(old, new):
        left = set(reference[i].argsort()[-10:])
        right = set(components[j].argsort()[-10:])
        jaccards.append(len(left & right) / len(left | right))
    print("STABILITY", seed, "cosine_mean", float(np.mean(similarities)),
          "cosine_min", float(np.min(similarities)),
          "jaccard10_mean", float(np.mean(jaccards)),
          "jaccard10_min", float(np.min(jaccards)),
          "agreement", float(np.mean(reference_assignment == aligned_assignment)), flush=True)
    for i, j, score, jac in zip(old, new, similarities, jaccards):
        print("MATCH", seed, int(i), int(j), "cos", round(float(score), 3),
              "jaccard", round(float(jac), 3),
              "ref_share", round(float(np.mean(reference_assignment == i)), 4),
              "other_share", round(float(np.mean(assignment == j)), 4), flush=True)
```

### run-A-hypothesis_tests.py

```python
import csv
import math
import re
from collections import Counter

import numpy as np
from scipy import stats


path = "/home/elta/mj-ai-run-A/midjourney_prompts_all.csv"
filters = [
    re.compile(r"\s*\d+\s*:\s*\d+\s*"),
    re.compile(r"\s*\d+(?:\.\d+)?\s*"),
    re.compile(
        r"\s*(?:(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)"
        r"(?:\s+(?:--|[—–])[a-z][a-z0-9-]*(?:\s+(?!(?:--|[—–]))\S+)?)*\s*",
        re.I,
    ),
    re.compile(r"\s*https?://\S+\s*", re.I),
]
with open(path, encoding="utf-8-sig", newline="") as file:
    texts = list(dict.fromkeys(
        row["text"] for row in csv.DictReader(file)
        if row["text"].strip() and not any(p.fullmatch(row["text"]) for p in filters)
    ))

artist_aliases = [
    "craig mullins", "peter mohrbacher", "tsutomu nihei", "floria sigismondi",
    "robert mapplethorpe", "ashley wood", "hajime sorayama", "sarah morris",
    "annie leibovitz", "wlop", "hokusai", "hayao miyazaki", "ansel adams",
    "joel meyerowitz", "karel thole", "alphonse mucha", "alfons mucha", "mucha",
    "james jean", "renato muccillo", "artgerm", "thomas kinkade", "thomas kindkade",
    "katsuhiro otomo", "jean-honoré fragonard", "jean-honore fragonard",
    "harumi hironaka", "charlie bowater", "mœbius", "moebius", "jean giraud",
    "greg rutkowski", "kilian eng", "marc simonetti", "gustave dore", "gustave doré",
    "beeple", "tom bagshaw", "andrei riabovitchev", "ross tran", "yoshitaka amano",
    "yoji shinkawa", "tim burton", "tim walker", "wes anderson", "norman rockwell",
    "makoto shinkai", "emil melmoth", "james gurney", "syd mead", "filip hodas",
    "stefan gesell", "jean-michel basquiat", "basquiat", "yousuf karsh",
    "hr giger", "h.r. giger", "giger", "zdzisław beksiński", "zdzislaw beksinski",
    "beksinski", "beksinkski", "vincent van gogh", "van gogh",
]


def literal(s):
    return r"(?<!\w)" + r"\s+".join(re.escape(x) for x in s.split()) + r"(?!\w)"


artist = re.compile("|".join(literal(s) for s in artist_aliases), re.I)
quality_phrases = [
    "trending on artstation", "8k", "octane render",
    "highly detailed", "4k", "unreal engine",
]
quality = re.compile("|".join(literal(s) for s in quality_phrases), re.I)
has_parameter = re.compile(r"(?<!\S)(?:--|[—–])[a-z][a-z0-9-]*", re.I)
parameter = re.compile(
    r"(?<!\S)(?:--|[—–])([a-z][a-z0-9-]*)"
    r"(?:\s+(?!(?:--|[—–]))(\S+))?",
    re.I,
)
value_options = {
    "ar", "aspect", "w", "h", "stop", "seed", "iw", "no", "style",
    "q", "quality", "s", "stylize", "v", "version", "chaos", "c",
}


def remove_option(match):
    name, value = match.groups()
    return " " if value is None or name.lower() in value_options else " " + value


def test_lengths(lengths, group, label):
    x = lengths[group]
    y = lengths[~group]
    result = stats.mannwhitneyu(x, y, alternative="greater", method="asymptotic")
    ties = np.array(list(Counter(lengths).values()), dtype=np.float64)
    n1, n0 = len(x), len(y)
    n = n1 + n0
    variance = n1 * n0 / 12 * (n + 1 - np.sum(ties ** 3 - ties) / (n * (n - 1)))
    z = (result.statistic - n1 * n0 / 2 - 0.5) / math.sqrt(variance)
    print(label, "n1", n1, "n0", n0, "mean1", x.mean(), "mean0", y.mean(),
          "median1", np.median(x), "median0", np.median(y), "U", result.statistic,
          "p", result.pvalue, "log10p", stats.norm.logsf(z) / math.log(10),
          "prob_superiority", result.statistic / (n1 * n0),
          "rank_biserial", 2 * result.statistic / (n1 * n0) - 1,
          "mean_difference", x.mean() - y.mean(), flush=True)


group = np.array([bool(has_parameter.search(t)) for t in texts])
full_lengths = np.array([len(t.split()) for t in texts])
body_lengths = np.array([len(parameter.sub(remove_option, t).split()) for t in texts])
print("DATA", len(texts), "PARAMS", int(group.sum()), "ARTIST", sum(bool(artist.search(t)) for t in texts),
      "QUALITY", sum(bool(quality.search(t)) for t in texts))
test_lengths(full_lengths, group, "H1_FULL")
test_lengths(body_lengths, group, "H1_WITHOUT_OPTIONS")

artist_group = np.array([bool(artist.search(t)) for t in texts])
quality_group = np.array([bool(quality.search(t)) for t in texts])
a = int(np.sum(artist_group & quality_group))
b = int(np.sum(artist_group & ~quality_group))
c = int(np.sum(~artist_group & quality_group))
d = int(np.sum(~artist_group & ~quality_group))
chi2, p, dof, expected = stats.chi2_contingency([[a, b], [c, d]], correction=False)
odds_ratio = a * d / (b * c)
se_log_or = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
low, high = (math.exp(math.log(odds_ratio) + sign * 1.96 * se_log_or) for sign in (-1, 1))
log10p = (math.log(2) + stats.norm.logsf(math.sqrt(chi2))) / math.log(10)
print("H2", "table", [[a, b], [c, d]], "chi2", chi2, "df", dof, "p", p,
      "log10p", log10p, "odds_ratio", odds_ratio, "odds_ratio_ci95", [low, high],
      "artist_rate", a / (a + b), "other_rate", c / (c + d),
      "risk_difference", a / (a + b) - c / (c + d),
      "risk_ratio", (a / (a + b)) / (c / (c + d)),
      "expected", expected.tolist(), flush=True)
```

### run-A-reproduce_all.py

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
