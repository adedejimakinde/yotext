"""Build a normalization training/eval dataset from corrupted Yorùbá Wikipedia sentences."""

import glob
import json
import os
import random
import unicodedata

import corrupt
from yotext import standardize, diacritic_coverage

COVERAGE_THRESHOLD = 0.75
MIN_SENTENCE_LEN = 20
MAX_SENTENCE_LEN = 200
MAX_SENTENCES = 3000
SHUFFLE_SEED = 0
OUTPUT_PATH = "data/normalization_pairs.jsonl"
SOURCE = "yowiki"


def split_sentences(text):
    sentences = []
    current = []
    for ch in text:
        if ch in ".!?":
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)
            current = []
        else:
            current.append(ch)
    sentence = "".join(current).strip()
    if sentence:
        sentences.append(sentence)
    return sentences


def has_combining_mark(sentence):
    nfd = unicodedata.normalize("NFD", sentence)
    return any(unicodedata.combining(c) != 0 for c in nfd)


def collect_sentences():
    seen = set()
    for path in glob.glob("corpus/extracted/*/wiki_*"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                doc = json.loads(line)
                text = doc["text"]
                if diacritic_coverage(text) < COVERAGE_THRESHOLD:
                    continue
                for sentence in split_sentences(text):
                    if not (MIN_SENTENCE_LEN <= len(sentence) <= MAX_SENTENCE_LEN):
                        continue
                    if not has_combining_mark(sentence):
                        continue
                    seen.add(sentence)
    return list(seen)


def main():
    sentences = collect_sentences()
    random.Random(SHUFFLE_SEED).shuffle(sentences)
    sentences = sentences[:MAX_SENTENCES]

    os.makedirs("data", exist_ok=True)

    record_count = 0
    issue_counts = {kind: 0 for kind in corrupt.CORRUPTIONS}

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        for i, sentence in enumerate(sentences):
            canonical = standardize(sentence)
            for kind in corrupt.CORRUPTIONS:
                raw = corrupt.corrupt(sentence, kind, seed=SHUFFLE_SEED + i)
                if raw == canonical:
                    continue
                record = {
                    "raw": raw,
                    "canonical": canonical,
                    "issue": kind,
                    "source": SOURCE,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                record_count += 1
                issue_counts[kind] += 1

    print(f"sentences: {len(sentences)}")
    print(f"records: {record_count}")
    for kind in corrupt.CORRUPTIONS:
        print(f"  {kind}: {issue_counts[kind]}")


if __name__ == "__main__":
    main()
