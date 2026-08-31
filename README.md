# yotext

Orthographic normalization and diacritic handling for Yorùbá text. Zero runtime dependencies. Requires Python 3.9 or newer.

## Why this exists

Yorùbá text in circulation is encoded inconsistently. The underdot that marks ẹ, ọ, and ṣ shows up as U+0323, U+0329, U+0331, or U+032D depending on the keyboard and the era it was typed on. Combining marks often arrive out of canonical order too. The same word ends up as several different byte sequences that look identical on screen and compare unequal in code. `standardize()` folds all of that into one canonical form.

## Tone marks and underdots are different things

This is the part that matters most. The underdot in ẹ, ọ, and ṣ is segmental. ẹ and e are separate phonemes, and removing the underdot turns one word into a different word. Tone marks, the acute in á and the grave in à, are suprasegmental. They mark pitch on top of a vowel, and they do not change which phoneme the vowel is.

Most text preprocessing code lumps both of these under the single label "diacritics" and strips them together. That conflates two different linguistic categories, and it produces wrong output for any task that depends on the ẹ/e or ọ/o distinction.

`strip_tones()` removes tone marks and keeps the underdot. `strip_diacritics()` removes both. I kept both functions because they answer different questions, and code that only offers one of them is answering the wrong question at least some of the time.

## Install

```
pip install yotext
```

## Usage

```python
from yotext import standardize, strip_tones, strip_diacritics, tone_pattern

# Messy input: wrong underdot codepoint (U+0329 instead of U+0323)
# and a tone mark placed before the underdot instead of after.
messy = "e\u0300\u0329ko\u0301\u0331"
standardize(messy)
# 'ẹ̀kọ́'

strip_tones("ẹ̀kọ́")
# 'ẹkọ'  tone dropped, underdot kept, ẹ and e stay different words

strip_diacritics("ẹ̀kọ́")
# 'eko'  fully undiacritized, the baseline used in ablation experiments

tone_pattern("bàbá")
# 'LH'  useful for checking tone distribution across a corpus
```

Two strings can look identical and still compare unequal, if one uses a precomposed vowel and the other uses a decomposed one with a non-canonical underdot codepoint.

```python
s1 = "\u1eb9"       # precomposed ẹ
s2 = "e\u0329"      # decomposed, non-canonical underdot
s1 == s2                       # False
standardize(s1) == standardize(s2)  # True
```

Running `standardize()` on a corpus before deduplicating or indexing it collapses these variants so equal words compare equal.

## What it guarantees

`standardize()` is idempotent. Running it twice gives the same result as running it once.

`strip_diacritics(s)` equals `strip_diacritics(strip_tones(s))` for any input. Removing tone first and then removing what remains lands on the same undiacritized form as removing everything at once.

Combining marks always come out in canonical order, combining class 220 before combining class 230.

## What it does not do

Version 0.1 does normalization only. It does not restore diacritics. Predicting bẹ̀rẹ̀ from bere, meaning guessing which vowels carry an underdot or a tone mark from plain ASCII input, is not implemented. That is planned for a later release.

## License

MIT.
