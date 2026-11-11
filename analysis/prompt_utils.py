"""Rules for turning a raw Midjourney prompt into variables.

Every rule the paper reports is defined here, so the paper can quote it
exactly and anyone can check it. Change a rule here, re-run pipeline.py,
and every table and figure updates.
"""
import re

# Midjourney parameters are written "--name value". Phones and Discord often
# turn "--" into an en or em dash, so accept any of them.
DASH = r"(?:--|—|–|-—|—-)"
PARAM_RE = re.compile(DASH + r"\s?([A-Za-z]+)(?:\s+([^\s-][^\s]*))?")

# Known parameter names, mapped to one canonical name. Anything else is "other".
PARAM_CANON = {
    "ar": "aspect", "aspect": "aspect",
    "w": "width", "h": "height",
    "no": "no",
    "stop": "stop",
    "seed": "seed", "sameseed": "seed",
    "iw": "image_weight",
    "uplight": "uplight", "upligh": "uplight",
    "test": "test", "tes": "test",
    "hd": "hd",
    "fast": "fast", "vibefast": "fast",
    "vibe": "vibe",
    "video": "video",
    "wallpaper": "wallpaper",
    "style": "style",
}

URL_RE = re.compile(r"https?://\S+|<https?://[^>]+>")
ASPECT_ONLY_RE = re.compile(r"^\s*\d{1,2}\s*:\s*\d{1,2}\s*$")
NUMBER_ONLY_RE = re.compile(r"^\s*[\d.,:]+\s*$")
WEIGHT_RE = re.compile(r"::\s*-?\d*\.?\d*")
WORD_RE = re.compile(r"[a-z][a-z'\-]*")

# Artist / style references. Two versions, so the paper can show how much the
# answer depends on the rule (a measurement-validity point):
#   strict  - "by" or "in the style of" followed by Capitalised Words
#   lenient - same cue words, any case, up to 4 words, split on "and" / ","
ARTIST_STRICT_RE = re.compile(
    r"\b(?:by|in the style of|style of)\s+((?:[A-Z][\w.'\-]+)(?:\s+[A-Z][\w.'\-]+){0,3})"
)
ARTIST_CUE_RE = re.compile(
    r"\b(?:by|in the style of|style of)\s+([^,|;:+\n]{2,80})", re.IGNORECASE
)
SPLIT_NAMES_RE = re.compile(r"\s*(?:,|\band\b|&|\+)\s*", re.IGNORECASE)
NOT_A_NAME = {
    "the", "a", "an", "my", "his", "her", "their", "its", "this", "that", "night",
    "day", "light", "moonlight", "sunlight", "candlelight", "itself", "water",
    "side", "itself", "people", "fire", "trees", "children", "hand", "me",
}

# "Quality booster" phrases: words added to push image quality rather than
# describe content. Matched case-insensitively as whole phrases.
BOOSTERS = [
    "trending on artstation", "artstation", "octane render", "unreal engine",
    "highly detailed", "hyper detailed", "hyperdetailed", "intricate",
    "hyperrealistic", "hyper realistic", "photorealistic", "ultra realistic",
    "8k", "4k", "16k", "hd", "uhd", "cinematic", "volumetric lighting",
    "volumetric light", "concept art", "masterpiece", "award winning",
    "sharp focus", "ray tracing", "dramatic lighting", "studio lighting",
]
BOOSTER_RES = {b: re.compile(r"(?<![a-z0-9])" + re.escape(b) + r"(?![a-z0-9])") for b in BOOSTERS}


def normalise(text: str) -> str:
    """Lower-case and collapse whitespace; used to find duplicates."""
    return " ".join(text.lower().split())


def params(text: str):
    """Return a list of (canonical_name, value) for each parameter."""
    out = []
    for name, value in PARAM_RE.findall(text):
        out.append((PARAM_CANON.get(name.lower(), "other"), value or ""))
    return out


def aspect_ratio(text: str):
    """Return the --ar / --aspect value as 'W:H', or None."""
    for name, value in params(text):
        if name == "aspect" and re.match(r"^\d+:\d+$", value):
            return value
    return None


def content_text(text: str) -> str:
    """Prompt text with parameters, URLs and :: weights removed."""
    t = URL_RE.sub(" ", text)
    t = PARAM_RE.sub(" ", t)
    t = WEIGHT_RE.sub(" ", t)
    return " ".join(t.split())


def content_words(text: str):
    return WORD_RE.findall(content_text(text).lower())


def fragment_type(text: str) -> str:
    """Classify a row. Anything other than 'prompt' is excluded from the clean prompts.

    Order matters: the first matching rule wins.
    """
    s = text.strip()
    if not s:
        return "empty"
    if ASPECT_ONLY_RE.match(s):
        return "aspect_ratio_only"
    if NUMBER_ONLY_RE.match(s):
        return "number_only"
    stripped = content_text(s)
    if not stripped:
        return "url_or_params_only"
    n = len(content_words(s))
    if n == 0:
        return "symbols_only"
    if n < MIN_CONTENT_WORDS:
        return "short_fragment"
    return "prompt"


# A row needs at least this many content words to count as a prompt.
MIN_CONTENT_WORDS = 3


def artists(text: str, mode: str = "lenient"):
    """Return the artist / style names referenced in a prompt (lower-cased).

    Works on the content text, so a trailing parameter or :: weight is not
    read as part of a name ("by ashley wood --ar 9:16" is "ashley wood",
    not "ashley wood ar").
    """
    text = content_text(text)
    if mode == "strict":
        names = [m.strip() for m in ARTIST_STRICT_RE.findall(text)]
    else:
        names = []
        for chunk in ARTIST_CUE_RE.findall(text):
            for part in SPLIT_NAMES_RE.split(chunk):
                words = [w for w in WORD_RE.findall(part.lower()) if len(w) > 1][:4]
                if words:
                    names.append(" ".join(words))
    clean = []
    for n in names:
        n = n.lower().strip(" .'-")
        if len(n) < 3 or n.split()[0] in NOT_A_NAME:
            continue
        clean.append(n)
    return clean


def boosters(text: str):
    t = text.lower()
    return [b for b, rx in BOOSTER_RES.items() if rx.search(t)]
