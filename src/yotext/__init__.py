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
    "__version__",
]
