"""Orthographic standardization utilities for Yorùbá text."""

import unicodedata

from .constants import INVISIBLES, PUNCT_FIXES, UNDERDOT_VARIANTS


def standardize(text: str, *, compose: bool = True) -> str:
    """Normalize Yorùbá text to a canonical orthographic form.

    Invisible characters are dropped, smart quotes/dashes are replaced with
    their plain ASCII equivalents, and non-canonical combining-below marks
    are folded onto the canonical DOT_BELOW. The text is renormalized to NFD
    a second time after that substitution because swapping one combining
    mark for another can leave the combining-mark sequence out of Unicode
    canonical order: combining class 220 (below) must sort before combining
    class 230 (above), and a substituted mark does not automatically end up
    in the right position relative to its neighbors. Re-running NFD
    canonically reorders the sequence so the result composes correctly.

    Args:
        text: The input text.
        compose: If True (default), return the NFC form. If False, return
            the NFD form.

    Returns:
        The standardized text, in NFC or NFD form depending on `compose`.
    """
    text = text.translate(INVISIBLES)
    for old, new in PUNCT_FIXES.items():
        text = text.replace(old, new)
    text = unicodedata.normalize("NFD", text)
    for old, new in UNDERDOT_VARIANTS.items():
        text = text.replace(old, new)
    text = unicodedata.normalize("NFD", text)
    return unicodedata.normalize("NFC", text) if compose else text
