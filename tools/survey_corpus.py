"""Survey a wiki-extracted corpus for diacritic coverage."""

import glob
import json

from yotext import diacritic_coverage

MIN_CHARS = 300
DIACRITIC_THRESHOLD = 0.55


def main():
    total = 0
    kept = 0
    kept_tokens = 0

    for path in glob.glob("corpus/extracted/*/wiki_*"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                doc = json.loads(line)
                text = doc["text"]
                if len(text) < MIN_CHARS:
                    continue
                total += 1
                if diacritic_coverage(text) >= DIACRITIC_THRESHOLD:
                    kept += 1
                    kept_tokens += len(text.split())

    percentage = (kept / total * 100) if total else 0.0
    print(f"kept {kept}/{total} documents ({percentage:.1f}%)")
    print(f"kept token count: {kept_tokens:,}")


if __name__ == "__main__":
    main()
