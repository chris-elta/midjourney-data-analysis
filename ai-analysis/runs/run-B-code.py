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
    return [w for w in ws if re.search(r'[A-Za-zÀ-￿]', w)]

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
    print("cjk/cyrillic unique", sum(1 for t in set(T) if re.search(r'[぀-ヿ一-鿿가-힯Ѐ-ӿ]', t)))
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
R_BY = re.compile(r"(?:^|[,;:+|(\[]|\b" + ARTW + r"\b)\s*by\s+[a-zÀ-ɏ]")

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
        t = re.sub(r"[^a-zÀ-ɏ' ]+", ' ', t)                # letters only
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
        NAMES = {w for k in A for w in re.findall(r"[a-zà-ɏ]+", k.lower()) if len(w) > 2} | \
                {'mullins', 'mohrbacher', 'ghibli', 'studio', 'pixar', 'disney', 'giger', 'mucha', 'kinkade'}
        NAMES -= {'wood', 'grey', 'bacon', 'hopper', 'english', 'ware', 'bass', 'blake', 'dean', 'frank', 'walker', 'adams',
                  'morris', 'davis', 'howe', 'jean', 'ellis', 'williams', 'turner', 'gogh', 'grimmer', 'parr', 'bak', 'fate', 'leche',
                  'tran', 'eng', 'jia', 'zhu', 'witz', 'bowater', 'billy', 'butcher', 'flores', 'scott', 'bosch', 'mead', 'foss',
                  'friedrich', 'david', 'caspar', 'mary', 'john', 'saul', 'alex', 'don', 'mike', 'roger', 'tim', 'tom', 'james'}
        STOP |= set(STYLE) | NAMES
    STOP = list(STOP)
    TOK = r"(?u)\b[a-zÀ-ɏ][a-zÀ-ɏ']+\b"
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
