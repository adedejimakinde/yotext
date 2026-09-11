"""Command line interface for yotext."""

import argparse
import json
import sys
from pathlib import Path

from . import restore
from .docx import read_docx, process_docx
from .standardize import standardize
from .tones import strip_tones, strip_diacritics
from .validate import validate
from .variants import variants, inconsistent


def _is_docx(path):
    return path not in (None, "-") and Path(path).suffix.lower() == ".docx"


def _read_input(path):
    if path is None or path == "-":
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="yotext",
        description="Orthographic normalization and diacritic handling for Yorùbá text.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser(
        "normalize", help="Standardize text and write it to stdout."
    )
    normalize_parser.add_argument("path", nargs="?", default=None)
    normalize_parser.add_argument(
        "--output", default=None, help="Write to this path instead of stdout. Required for .docx input."
    )
    exclusive = normalize_parser.add_mutually_exclusive_group()
    exclusive.add_argument("--strip-tones", action="store_true")
    exclusive.add_argument("--strip-diacritics", action="store_true")
    normalize_parser.set_defaults(func=_cmd_normalize)

    validate_parser = subparsers.add_parser(
        "validate", help="Report orthographic issues found in text."
    )
    validate_parser.add_argument("path", nargs="?", default=None)
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.set_defaults(func=_cmd_validate)

    variants_parser = subparsers.add_parser(
        "variants", help="Show diacritic variants of the same bare word form."
    )
    variants_parser.add_argument("path", nargs="?", default=None)
    variants_parser.add_argument("--min-count", type=int, default=2)
    variants_parser.add_argument("--all", action="store_true")
    variants_parser.set_defaults(func=_cmd_variants)

    restore_parser = subparsers.add_parser(
        "restore", help="Restore diacritics and write the result to stdout."
    )
    restore_parser.add_argument("path", nargs="?", default=None)
    restore_parser.set_defaults(func=_cmd_restore)

    return parser


def _cmd_normalize(args) -> int:
    def transform(text):
        result = standardize(text)
        if args.strip_tones:
            result = strip_tones(result)
        elif args.strip_diacritics:
            result = strip_diacritics(result)
        return result

    if _is_docx(args.path):
        if args.output is None:
            print(
                "yotext: normalizing a .docx file writes a new document, so it needs --output PATH",
                file=sys.stderr,
            )
            return 1
        process_docx(args.path, args.output, transform)
        return 0

    result = transform(_read_input(args.path))
    if args.output is None:
        sys.stdout.write(result)
    else:
        Path(args.output).write_text(result, encoding="utf-8")
    return 0


def _cmd_validate(args) -> int:
    text = read_docx(args.path) if _is_docx(args.path) else _read_input(args.path)
    report = validate(text)
    if args.json:
        payload = {
            "length": report.length,
            "coverage": report.coverage,
            "non_canonical_underdots": report.non_canonical_underdots,
            "misordered_marks": report.misordered_marks,
            "invisibles": report.invisibles,
            "smart_punctuation": report.smart_punctuation,
            "is_canonical": report.is_canonical,
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(report.summary() + "\n")
    return 0


def _cmd_variants(args) -> int:
    text = _read_input(args.path)
    lookup = variants if args.all else inconsistent
    result = lookup(text, min_count=args.min_count)
    ordered = sorted(result.items(), key=lambda item: sum(item[1].values()), reverse=True)
    for bare, forms in ordered:
        forms_str = ", ".join(f"{form}={count}" for form, count in forms.items())
        sys.stdout.write(f"{bare}: {forms_str}\n")
    return 0


def _cmd_restore(args) -> int:
    if _is_docx(args.path):
        print(
            "yotext: restore does not support .docx files yet. A single word can be "
            "split across several formatting runs, so restoring run by run would "
            "predict diacritics from fragments instead of whole words. Extract the "
            "text first and restore that.",
            file=sys.stderr,
        )
        return 1
    text = _read_input(args.path)
    sys.stdout.write(restore(text))
    return 0


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"yotext: {exc.filename}: No such file or directory", file=sys.stderr)
        return 1
    except ImportError as exc:
        print(f"yotext: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
