---
license: cc-by-sa-4.0
language:
  - yo
task_categories:
  - text-generation
tags:
  - yoruba
  - unicode
  - text-normalization
  - diacritics
  - african-languages
  - low-resource
size_categories:
  - 10K<n<100K
configs:
  - config_name: default
    data_files: normalization_pairs.jsonl
---

# Normalization pairs dataset

## What this is

24,475 pairs of Yorùbá text, each a corrupted form next to its canonical form, labelled by corruption type. I built it for testing orthographic normalization code.

## Format

JSON Lines, UTF-8. Each line is one object with four fields: raw, canonical, issue, source.

```json
{"raw": "Os̩ù ké̩rin o̩dún 2020", "canonical": "Oṣù kẹ́rin ọdún 2020", "issue": "underdot_0329", "source": "yowiki"}
```

## Corruption types

| Type | Description | Records |
|---|---|---|
| underdot_0329 | Underdot written as the non-canonical combining vertical line below (U+0329) instead of U+0323. | 3000 |
| underdot_0331 | Underdot written as the non-canonical combining macron below (U+0331) instead of U+0323. | 3000 |
| underdot_032D | Underdot written as the non-canonical combining circumflex below (U+032D) instead of U+0323. | 3000 |
| reorder_marks | Tone mark placed before the underdot on the same letter, out of canonical combining order. | 3000 |
| decompose | Text left in NFD form instead of NFC. | 3000 |
| inject_invisibles | Zero-width and soft-hyphen characters inserted at a few positions. | 3000 |
| smart_punctuation | Straight quotes turned into curly quotes, hyphens between words turned into en dashes. | 475 |
| strip_tone_only | Tone marks removed, underdot kept. | 3000 |
| strip_all_diacritics | Every combining mark removed, tone and underdot alike. | 3000 |

smart_punctuation only applies to sentences that already contain a quote or a hyphen, so it produced far fewer records than the other types.

## How it was built

3000 sentences were sampled from Yorùbá Wikipedia articles with diacritic coverage at or above 0.75, deduplicated, and selected with a seeded shuffle so the sample is reproducible. Each corruption was applied by tools/corrupt.py. That script deliberately does not import yotext, so a bug in the library cannot make this dataset quietly agree with it.

## The two lossy types

strip_tone_only and strip_all_diacritics destroy information. Once tone marks or underdots are gone, no normalization function can restore them, since the information about which vowel or tone was there no longer exists in the string. These two types are included for evaluating restoration, not normalization.

## License

The text comes from Yorùbá Wikipedia, which is licensed CC BY-SA 4.0. This dataset is therefore CC BY-SA 4.0 too, and attributes Wikipedia as the source. This differs from the MIT license that covers the code in this repository. Check which license applies before reusing either one.

## Limitations

All the corruptions here are synthetic. Real Yorùbá text contains encoding failures nobody would think to simulate, and none of those are represented here. The source is a single domain, encyclopedic prose from Wikipedia, so the dataset says nothing about how this code performs on social media posts, chat messages, or other informal writing. A version built from naturally occurring errors would be more valuable than this one, and it does not exist yet.
