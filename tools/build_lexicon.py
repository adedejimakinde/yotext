"""Build a diacritization lexicon from a wiki-extracted corpus."""

import glob
import gzip
import hashlib
import json
import os
from collections import Counter, defaultdict

from yotext import standardize, strip_diacritics, diacritic_coverage

MIN_CHARS = 300
TRAIN_THRESHOLD = 0.55
TEST_THRESHOLD = 0.75
PUNCTUATION = ".,!?;:\"'()[]"
MAX_CANDIDATES = 8
OUTPUT_PATH = "src/yotext/data/lexicon.json.gz"
TEST_FRACTION = 0.05
TEST_SPLIT_PATH = "corpus/test_split.jsonl"


def tokenize(text):
    tokens = []
    for raw in standardize(text).split():
        word = raw.strip(PUNCTUATION).lower()
        if word:
            tokens.append(word)
    return tokens


def is_test(title):
    digest = hashlib.md5(title.encode("utf-8")).hexdigest()
    return int(digest, 16) % 100 < TEST_FRACTION * 100


def main():
    unigram = defaultdict(Counter)
    bigram = Counter()
    train_count = 0
    test_kept_count = 0
    test_discarded_count = 0

    with open(TEST_SPLIT_PATH, "w", encoding="utf-8") as test_file:
        for path in glob.glob("corpus/extracted/*/wiki_*"):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    doc = json.loads(line)
                    text = doc["text"]
                    if len(text) < MIN_CHARS:
                        continue

                    title = doc["title"]
                    coverage = diacritic_coverage(text)

                    if is_test(title):
                        if coverage < TEST_THRESHOLD:
                            test_discarded_count += 1
                            continue
                        test_kept_count += 1
                        test_file.write(
                            json.dumps({"title": title, "text": text}, ensure_ascii=False)
                            + "\n"
                        )
                        continue

                    if coverage < TRAIN_THRESHOLD:
                        continue

                    train_count += 1
                    tokens = tokenize(text)

                    prev = "<s>"
                    for word in tokens:
                        bare = strip_diacritics(word)
                        unigram[bare][word] += 1
                        if prev != "<s>":
                            bigram[(prev, word)] += 1
                        prev = word

    pruned_unigram = {}
    for bare, counter in unigram.items():
        if sum(counter.values()) == 1:
            continue
        pruned_unigram[bare] = dict(counter.most_common(MAX_CANDIDATES))

    pruned_bigram = {
        f"{a}\t{b}": count
        for (a, b), count in bigram.items()
        if count > 1
    }

    data = {"unigram": pruned_unigram, "bigram": pruned_bigram}

    with gzip.open(OUTPUT_PATH, "wt", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"train documents used: {train_count}")
    print(f"test documents kept: {test_kept_count}")
    print(f"test documents discarded for low coverage: {test_discarded_count}")
    print(f"bare forms: {len(pruned_unigram)}")
    print(f"bigrams: {len(pruned_bigram)}")
    print(f"output size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
