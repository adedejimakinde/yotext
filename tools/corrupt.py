"""Generate corrupted Yorùbá text variants for testing normalization independently of yotext."""

import random
import unicodedata

DOT_BELOW = "̣"
TONE_MARKS = {"́", "̀", "̄"}
INVISIBLE_CHARS = ["​", "‌", "­"]

CORRUPTIONS = [
    "underdot_0329",
    "underdot_0331",
    "underdot_032D",
    "reorder_marks",
    "decompose",
    "inject_invisibles",
    "smart_punctuation",
    "strip_tone_only",
    "strip_all_diacritics",
]


def underdot_0329(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return nfd.replace(DOT_BELOW, "̩")


def underdot_0331(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return nfd.replace(DOT_BELOW, "̱")


def underdot_032D(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return nfd.replace(DOT_BELOW, "̭")


def reorder_marks(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    result = []
    i = 0
    n = len(nfd)
    while i < n:
        ch = nfd[i]
        if unicodedata.combining(ch) != 0:
            result.append(ch)
            i += 1
            continue
        base = ch
        i += 1
        marks = []
        while i < n and unicodedata.combining(nfd[i]) != 0:
            marks.append(nfd[i])
            i += 1
        if DOT_BELOW in marks and any(m in TONE_MARKS for m in marks):
            tone = [m for m in marks if m in TONE_MARKS]
            rest = [m for m in marks if m not in TONE_MARKS]
            marks = tone + rest
        result.append(base)
        result.extend(marks)
    return "".join(result)


def decompose(text: str) -> str:
    return unicodedata.normalize("NFD", text)


def inject_invisibles(text: str) -> str:
    if not text:
        return text
    chars = list(text)
    num_insertions = min(3, len(chars) + 1)
    positions = sorted(random.sample(range(len(chars) + 1), num_insertions), reverse=True)
    for pos in positions:
        chars.insert(pos, random.choice(INVISIBLE_CHARS))
    return "".join(chars)


def smart_punctuation(text: str) -> str:
    result = []
    double_open = True
    single_open = True
    n = len(text)
    for i, ch in enumerate(text):
        if ch == '"':
            result.append("“" if double_open else "”")
            double_open = not double_open
        elif ch == "'":
            result.append("‘" if single_open else "’")
            single_open = not single_open
        elif ch == "-" and 0 < i < n - 1 and text[i - 1].isalnum() and text[i + 1].isalnum():
            result.append("–")
        else:
            result.append(ch)
    return "".join(result)


def strip_tone_only(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    filtered = "".join(c for c in nfd if c not in TONE_MARKS)
    return unicodedata.normalize("NFC", filtered)


def strip_all_diacritics(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if not unicodedata.combining(c))


_FUNCTIONS = {
    "underdot_0329": underdot_0329,
    "underdot_0331": underdot_0331,
    "underdot_032D": underdot_032D,
    "reorder_marks": reorder_marks,
    "decompose": decompose,
    "inject_invisibles": inject_invisibles,
    "smart_punctuation": smart_punctuation,
    "strip_tone_only": strip_tone_only,
    "strip_all_diacritics": strip_all_diacritics,
}


def corrupt(text: str, kind: str, seed: int = 0) -> str:
    random.seed(seed)
    return _FUNCTIONS[kind](text)


def all_corruptions(text: str, seed: int = 0) -> dict:
    return {kind: corrupt(text, kind, seed) for kind in CORRUPTIONS}
