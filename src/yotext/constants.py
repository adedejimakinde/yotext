"""Constants used across the yotext package."""

# Combining diacritical marks (Unicode combining characters).
#
# DOT_BELOW is SEGMENTAL: it distinguishes separate phonemes (e.g. e-dot-below
# vs e, o-dot-below vs o) and is part of the letter identity, not the tone.
# ACUTE, GRAVE, and MACRON are SUPRASEGMENTAL tone marks layered on top of a
# vowel/syllabic nasal to indicate pitch (high, low, mid). These two
# categories must never be conflated: stripping "diacritics" for
# tone-insensitive comparison must not strip DOT_BELOW, and
# normalizing/stripping underdots must not touch tone marks.
DOT_BELOW = "\u0323"
ACUTE     = "\u0301"
GRAVE     = "\u0300"
MACRON    = "\u0304"

# Suprasegmental tone marks only. Does not include DOT_BELOW, which is
# segmental (see note above).
TONE_MARKS = frozenset({ACUTE, GRAVE, MACRON})

# Non-canonical combining-below marks sometimes substituted for DOT_BELOW
# (e.g. by fonts, keyboards, or OCR), mapped to the canonical DOT_BELOW.
UNDERDOT_VARIANTS = {
    "\u0329": DOT_BELOW,
    "\u0331": DOT_BELOW,
    "\u032D": DOT_BELOW,
}

# Base Latin vowel letters (uppercase and lowercase), before any diacritics.
VOWELS = frozenset("aeiouAEIOU")

# Syllabic nasal consonant letters (uppercase and lowercase).
NASALS = frozenset("nmNM")

# Invisible/zero-width Unicode characters to strip during cleanup, mapped
# via str.translate (values are None to delete).
INVISIBLES = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff\u00ad"), None)

# Typographic punctuation variants normalized to their plain ASCII forms.
PUNCT_FIXES = {
    "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-",
}
