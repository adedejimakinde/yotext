"""yotext: orthographic normalization and diacritic handling for Yorùbá text.

Provides text standardization, tone-mark stripping/extraction, and
diacritic handling for Yorùbá orthography.
"""

from .standardize import standardize
from .tones import strip_tones, strip_diacritics, tone_pattern, diacritic_coverage

__version__ = "0.1.0"
__all__ = [
    "standardize",
    "strip_tones",
    "strip_diacritics",
    "tone_pattern",
    "diacritic_coverage",
    "restore",
    "__version__",
]

_restorer = None


def restore(text: str) -> str:
    """Restore diacritics on text, loading the lexicon on first use.

    The lexicon is 1.5 MB, so it is loaded lazily on first call rather than
    at import time, to keep `import yotext` fast.
    """
    global _restorer
    if _restorer is None:
        from ._restore import LexiconRestorer

        _restorer = LexiconRestorer()
    return _restorer.restore(text)
