"""Tests for yotext.cli."""

import json

import pytest

from yotext.cli import main


def _write(tmp_path, content):
    path = tmp_path / "input.txt"
    path.write_text(content, encoding="utf-8")
    return path


def test_normalize_writes_canonical_output(tmp_path, capsys):
    path = _write(tmp_path, "e\u0300\u0329ko\u0301\u0331")

    code = main(["normalize", str(path)])

    assert code == 0
    assert capsys.readouterr().out == "\u1eb9\u0300k\u1ecd\u0301"


def test_normalize_strip_tones(tmp_path, capsys):
    path = _write(tmp_path, "e\u0300\u0329ko\u0301\u0331")

    code = main(["normalize", "--strip-tones", str(path)])

    assert code == 0
    assert capsys.readouterr().out == "\u1eb9k\u1ecd"


def test_normalize_strip_diacritics(tmp_path, capsys):
    path = _write(tmp_path, "e\u0300\u0329ko\u0301\u0331")

    code = main(["normalize", "--strip-diacritics", str(path)])

    assert code == 0
    assert capsys.readouterr().out == "eko"


def test_strip_flags_are_mutually_exclusive(tmp_path, capsys):
    path = _write(tmp_path, "plain text")

    with pytest.raises(SystemExit) as exc_info:
        main(["normalize", "--strip-tones", "--strip-diacritics", str(path)])

    assert exc_info.value.code == 2
    assert "not allowed with argument" in capsys.readouterr().err


def test_validate_prints_report(tmp_path, capsys):
    path = _write(tmp_path, "e\u0300\u0329ko\u0301\u0331")

    code = main(["validate", str(path)])

    out = capsys.readouterr().out
    assert code == 0
    assert "length: 7 characters" in out
    assert "canonical: no" in out


def test_validate_json_is_parseable(tmp_path, capsys):
    path = _write(tmp_path, "e\u0300\u0329ko\u0301\u0331")

    code = main(["validate", "--json", str(path)])

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload["is_canonical"] is False
    assert payload["non_canonical_underdots"] == {"U+0329": 1, "U+0331": 1}


def test_variants_reports_inconsistent_forms(tmp_path, capsys):
    path = _write(tmp_path, "ni ni \u1eb9 e")

    code = main(["variants", str(path)])

    out = capsys.readouterr().out
    assert code == 0
    assert out == "e: \u1eb9=1, e=1\n"


def test_missing_file_returns_exit_code_one_without_raising(capsys):
    code = main(["normalize", "does_not_exist_abc.txt"])

    assert code == 1
    assert "No such file or directory" in capsys.readouterr().err


def test_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
