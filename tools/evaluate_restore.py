"""Evaluate diacritic restoration accuracy on the held-out test split."""

import gzip
import importlib.resources
import json

from yotext import standardize, strip_diacritics, restore

TEST_SPLIT_PATH = "corpus/test_split.jsonl"
ERRORS_PATH = "corpus/errors.tsv"
PUNCTUATION = ".,!?;:\"'()[]"
MAX_ERRORS = 200


def tokenize(text):
    tokens = []
    for raw in standardize(text).split():
        word = raw.strip(PUNCTUATION).lower()
        if word:
            tokens.append(word)
    return tokens


def load_unigram():
    resource = importlib.resources.files("yotext.data").joinpath("lexicon.json.gz")
    with resource.open("rb") as raw:
        with gzip.open(raw, "rt", encoding="utf-8") as f:
            data = json.load(f)
    return data["unigram"]


def main():
    unigram = load_unigram()

    total = 0
    correct_overall = 0
    ambiguous_total = 0
    ambiguous_correct = 0
    unambiguous_total = 0
    unambiguous_correct = 0
    oov_total = 0
    skipped_docs = 0
    errors = []

    with open(TEST_SPLIT_PATH, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            text = doc["text"]

            gold_tokens = tokenize(text)
            if not gold_tokens:
                continue

            bare_tokens = [strip_diacritics(t) for t in gold_tokens]
            undiacritized_text = " ".join(bare_tokens)
            restored_tokens = restore(undiacritized_text).split()

            if len(restored_tokens) != len(gold_tokens):
                skipped_docs += 1
                continue

            for bare, gold, predicted in zip(bare_tokens, gold_tokens, restored_tokens):
                total += 1
                candidates = unigram.get(bare)
                is_oov = candidates is None
                is_ambiguous = candidates is not None and len(candidates) > 1
                is_match = predicted == gold

                if is_oov:
                    oov_total += 1
                elif is_ambiguous:
                    ambiguous_total += 1
                    if is_match:
                        correct_overall += 1
                        ambiguous_correct += 1
                else:
                    unambiguous_total += 1
                    if is_match:
                        correct_overall += 1
                        unambiguous_correct += 1

                if not is_match and len(errors) < MAX_ERRORS:
                    errors.append((bare, gold, predicted))

    with open(ERRORS_PATH, "w", encoding="utf-8") as f:
        for bare, gold, predicted in errors:
            f.write(f"{bare}\t{gold}\t{predicted}\n")

    overall_accuracy = correct_overall / total if total else 0.0
    ambiguous_accuracy = ambiguous_correct / ambiguous_total if ambiguous_total else 0.0
    unambiguous_accuracy = unambiguous_correct / unambiguous_total if unambiguous_total else 0.0
    oov_rate = oov_total / total * 100 if total else 0.0

    print(f"skipped documents (token count mismatch): {skipped_docs}")
    print(f"total tokens evaluated: {total}")
    print(f"overall word accuracy: {overall_accuracy:.4f}")
    print(f"ambiguous in-vocab accuracy: {ambiguous_accuracy:.4f}")
    print(f"unambiguous in-vocab accuracy: {unambiguous_accuracy:.4f}")
    print(f"OOV rate: {oov_rate:.2f}%")


if __name__ == "__main__":
    main()
