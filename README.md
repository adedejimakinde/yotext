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

## Quickstart

Here is every function in one pass.

```python
from yotext import standardize, strip_tones, strip_diacritics, tone_pattern, restore

standardize("e\u0300\u0329ko\u0301\u0331")  # 'ẹ̀kọ́'
strip_tones("ẹ̀kọ́")                         # 'ẹkọ'
strip_diacritics("ẹ̀kọ́")                     # 'eko'
tone_pattern("bàbá")                         # 'LH'
restore("owo mi wa nile")                    # 'ọwọ́ mi wà nílé'
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

## Diacritic restoration

`restore()` predicts diacritics for plain, undiacritized Yorùbá input. It looks up each word in a lexicon built from Yorùbá Wikipedia, and when a bare form has more than one diacritized candidate, it chooses between them with a bigram-scored Viterbi decode over the whole sentence, not by looking at the word in isolation.

```python
from yotext import restore

restore("owo mi wa nile")
# predicts tone marks and underdots per token, choosing between
# candidates using the surrounding words when a bare form is ambiguous
```

On held-out Wikipedia articles, restore() gets 87.3% of words right. On the ambiguous words, the ones where the lexicon offers more than one candidate and the model actually has to choose, accuracy is 89.4%. 2.5% of tokens are out of vocabulary and pass through undiacritized.

The evaluation set only includes held-out articles with diacritic coverage above 0.75. Wikipedia articles with lower coverage are themselves incompletely diacritized, so they cannot serve as gold data. I would rather report a number on a smaller, clean evaluation set than a number that is quietly measuring against wrong answers.

These numbers describe Wikipedia-style prose. Accuracy on social media and conversational text will be lower, since that kind of writing looks nothing like the lexicon's source. Proper nouns are the main source of out-of-vocabulary failures, since names do not repeat often enough in the training text to end up in the lexicon. A neural restorer is the obvious next step, and the lexicon-based version here is meant as a solid, inspectable baseline in the meantime.

## Citation

If you use this library in research, please cite it.

```bibtex
@software{makinde_yotext_2026,
  author  = {Makinde, Adedeji},
  title   = {yotext: Orthographic normalization and diacritic handling for Yor\`ub\'a text},
  year    = {2026},
  version = {0.2.0},
  url     = {https://github.com/adedejimakinde/yotext}
}
```

## License

MIT.
