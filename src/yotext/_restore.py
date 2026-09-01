"""Diacritic restoration for Yorùbá text."""

import gzip
import importlib.resources
import json
import math
from typing import Protocol

from .standardize import standardize
from .tones import strip_diacritics

BIGRAM_WEIGHT = 1.5


class Restorer(Protocol):
    def restore(self, text: str) -> str: ...


class LexiconRestorer:
    """Restore diacritics using a unigram/bigram lexicon and Viterbi decoding."""

    def __init__(self, path=None):
        if path is None:
            resource = importlib.resources.files("yotext.data").joinpath("lexicon.json.gz")
            with resource.open("rb") as raw:
                with gzip.open(raw, "rt", encoding="utf-8") as f:
                    data = json.load(f)
        else:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        self.unigram = data["unigram"]
        self.bigram = data["bigram"]

    def candidates(self, bare):
        return self.unigram.get(bare, {bare: 1})

    def restore(self, text: str) -> str:
        standardized = standardize(text)
        tokens = standardized.split()
        if not tokens:
            return standardized

        trellis = []
        prev_scores = {"<s>": 0.0}

        for token in tokens:
            bare = strip_diacritics(token.lower())
            cands = self.candidates(bare)
            total = sum(cands.values())
            current_scores = {}
            current_backptrs = {}
            for cand, count in cands.items():
                best_score = None
                best_prev = None
                for prev_cand, prev_score in prev_scores.items():
                    bigram_key = f"{prev_cand}\t{cand}"
                    bigram_count = self.bigram.get(bigram_key, 0)
                    score = (
                        prev_score
                        + math.log(count / total)
                        + BIGRAM_WEIGHT * math.log1p(bigram_count)
                    )
                    if best_score is None or score > best_score:
                        best_score = score
                        best_prev = prev_cand
                current_scores[cand] = best_score
                current_backptrs[cand] = best_prev
            trellis.append(current_backptrs)
            prev_scores = current_scores

        best_final = max(prev_scores, key=prev_scores.get)
        restored = [None] * len(tokens)
        cand = best_final
        for i in range(len(tokens) - 1, -1, -1):
            restored[i] = cand
            cand = trellis[i][cand]

        words = []
        for original, cand in zip(tokens, restored):
            if original.isupper():
                words.append(cand.upper())
            elif original[:1].isupper():
                words.append(cand.capitalize())
            else:
                words.append(cand)

        return " ".join(words)
