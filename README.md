# yotext

Orthographic normalization and diacritic handling for Yorùbá text. Zero runtime dependencies. Requires Python 3.9 or newer.

- PyPI: https://pypi.org/project/yotext/
- Source: https://github.com/adedejimakinde/yotext
- Dataset: https://huggingface.co/datasets/adedejimakinde/yoruba-normalization-pairs
- Web demo: https://yotext-demo.onrender.com/

## Why I built this

I had just finished the experiments for a paper comparing zero-shot prompting against fine-tuned models on Yorùbá sentiment analysis. Part of that work involved stripping diacritics from the text. Writing that preprocessing, I kept hitting the same problem in every tool I looked at. They treated tone marks and the underdot in ẹ, ọ, ṣ as one category called "diacritics" and removed both together.

They are not the same thing. The underdot changes the word. ẹ and e are different letters. Tone marks sit on top of a vowel and do not change which word it is.

The encoding underneath turned out to be its own problem. The same word shows up as four different byte sequences depending on which keyboard typed it, and none of them look different on screen.

## Install

```
pip install yotext
```

## Quickstart

```python
from yotext import standardize, strip_tones, strip_diacritics, tone_pattern, restore, validate, inconsistent

standardize("e\u0300\u0329ko\u0301\u0331")  # 'ẹ̀kọ́'
strip_tones("ẹ̀kọ́")                         # 'ẹkọ'
strip_diacritics("ẹ̀kọ́")                     # 'eko'
tone_pattern("bàbá")                         # 'LH'
restore("owo mi wa nile")                    # 'ọwọ́ mi wà nílé'
validate("ẹ̀kọ́").is_canonical               # True
inconsistent(["ni ní ni"])                   # {'ni': {'ni': 2, 'ní': 1}}
```

## Command line

```
yotext normalize file.txt
yotext validate file.txt
yotext variants corpus.txt --min-count 2
yotext restore file.txt
```

Every command reads stdin when no path is given or the path is `-`. `validate` takes `--json`. `normalize` takes `--strip-tones` or `--strip-diacritics`.

## Tone marks and underdots

`strip_tones()` removes tone marks and keeps the underdot. `strip_diacritics()` removes both. Both functions are here because they answer different questions.

## Checking a corpus

`validate(text)` reports what is wrong with text as it stands, without changing it.

```python
from yotext import validate
print(validate("e\u0301\u0329k\u1ecd\u200b").summary())
```

```
length: 6 characters
diacritic coverage: 1.00
non-canonical underdots: {'U+0329': 1}
misordered marks: 1
invisible characters: {'U+200B': 1}
smart punctuation: 0
canonical: no
```

`inconsistent(texts)` returns the bare forms that appear with more than one diacritization. Running it over a small sample of Yorùbá Wikipedia surfaces over a thousand such forms.

## Diacritic restoration

`restore()` predicts diacritics for undiacritized input. It looks up each word in a lexicon built from Yorùbá Wikipedia, and chooses between candidates with a bigram-scored Viterbi decode over the sentence.

On held-out Wikipedia articles it gets 87.3% of words right, and 89.4% on the ambiguous words where the lexicon offers more than one candidate. 2.5% of tokens are out of vocabulary and pass through unchanged.

The evaluation set only includes held-out articles with diacritic coverage above 0.75. Articles below that are themselves incompletely diacritized and cannot serve as gold data.

Accuracy on social media and conversational text will be lower. Proper nouns are the main source of out-of-vocabulary failures.

## Word documents

```
pip install yotext[docx]
yotext validate document.docx
yotext normalize document.docx --output clean.docx
```

Character and paragraph formatting survive. Restoration on docx is not supported, because words can be split across formatting runs.

## What it guarantees

`standardize()` is idempotent. `strip_diacritics(s)` equals `strip_diacritics(strip_tones(s))` for any input. Combining marks always come out in canonical order, combining class 220 before class 230.

## Dataset

24,475 Yorùbá text pairs for testing normalization code, each a corrupted form alongside its canonical form, labelled by corruption type. CC BY-SA 4.0, since the text comes from Yorùbá Wikipedia.

https://huggingface.co/datasets/adedejimakinde/yoruba-normalization-pairs

## Related work

Ìrànlọ́wọ́ (https://pypi.org/project/iranlowo/) is an earlier utility library for Yorùbá text, with tools for normalization, corpus analysis, and neural diacritic restoration.

## Citation

```bibtex
@software{makinde_yotext_2026,
  author  = {Makinde, Adedeji},
  title   = {yotext: Orthographic normalization and diacritic handling for Yorùbá text},
  year    = {2026},
  version = {0.4.0},
  url     = {https://github.com/adedejimakinde/yotext}
}
```

## Author

Adedeji Makinde. I build tools for African language NLP.

## License

The code is MIT. The lexicon in `src/yotext/data/` is derived from Yorùbá Wikipedia and available under CC BY-SA 4.0.
