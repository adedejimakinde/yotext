"""Diagnostic analysis of Yorùbá text for orthographic issues."""

import unicodedata
from dataclasses import dataclass

from .constants import DOT_BELOW, TONE_MARKS, UNDERDOT_VARIANTS, INVISIBLES, PUNCT_FIXES
from .standardize import standardize
from .tones import diacritic_coverage


@dataclass(frozen=True)
class Report:
    length: int
    coverage: float
    non_canonical_underdots: dict[str, int]
    misordered_marks: int
    invisibles: dict[str, int]
    smart_punctuation: int
    is_canonical: bool

    def summary(self) -> str:
        lines = [
            f"length: {self.length} characters",
            f"diacritic coverage: {self.coverage:.2f}",
            f"non-canonical underdots: {self.non_canonical_underdots or 'none'}",
            f"misordered marks: {self.misordered_marks}",
            f"invisible characters: {self.invisibles or 'none'}",
            f"smart punctuation: {self.smart_punctuation}",
            f"canonical: {'yes' if self.is_canonical else 'no'}",
        ]
        return "\n".join(lines)


def _decompose_preserving_order(text: str) -> str:
    """Expand precomposed characters without reordering existing marks.

    unicodedata.normalize("NFD", text) always canonically reorders combining
    marks, which would hide the very misordering this module reports.
    Normalizing one character at a time expands any precomposed letter into
    its own (already correctly ordered) decomposition without letting the
    reordering pass look across character boundaries, so marks that were
    already separate in the input keep their original relative order.
    """
    return "".join(unicodedata.normalize("NFD", ch) for ch in text)


def _count_non_canonical_underdots(nfd: str) -> dict:
    counts = {}
    for variant in UNDERDOT_VARIANTS:
        count = nfd.count(variant)
        if count:
            counts[f"U+{ord(variant):04X}"] = count
    return counts


_UNDERDOT_LIKE = frozenset({DOT_BELOW, *UNDERDOT_VARIANTS})


def _count_misordered_marks(nfd: str) -> int:
    count = 0
    i = 0
    n = len(nfd)
    while i < n:
        ch = nfd[i]
        if unicodedata.combining(ch) != 0:
            i += 1
            continue
        i += 1
        marks = []
        while i < n and unicodedata.combining(nfd[i]) != 0:
            marks.append(nfd[i])
            i += 1
        underdot_indices = [j for j, m in enumerate(marks) if m in _UNDERDOT_LIKE]
        if underdot_indices:
            first_underdot = underdot_indices[0]
            if any(m in TONE_MARKS for m in marks[:first_underdot]):
                count += 1
    return count


def _count_invisibles(text: str) -> dict:
    counts = {}
    for codepoint in INVISIBLES:
        char = chr(codepoint)
        count = text.count(char)
        if count:
            counts[f"U+{codepoint:04X}"] = count
    return counts


def _count_smart_punctuation(text: str) -> int:
    return sum(text.count(ch) for ch in PUNCT_FIXES)


def validate(text: str) -> Report:
    """Analyse text for orthographic issues without altering it.

    Combining-mark issues are read off the NFD form of the input as given;
    standardize() is used only to compute is_canonical, since running it
    first would fix the very problems this function is meant to report.
    """
    nfd = _decompose_preserving_order(text)

    return Report(
        length=len(text),
        coverage=diacritic_coverage(text),
        non_canonical_underdots=_count_non_canonical_underdots(nfd),
        misordered_marks=_count_misordered_marks(nfd),
        invisibles=_count_invisibles(text),
        smart_punctuation=_count_smart_punctuation(text),
        is_canonical=text == standardize(text),
    )
