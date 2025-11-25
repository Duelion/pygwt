from pathlib import Path

from pygwt.parser import GwtParser


def test_parse_examples(gwt_file, gwt_models):
    text = Path(gwt_file).read_text(encoding="utf-8")
    parser = GwtParser(text, gwt_models)
    result = parser.parse()
    assert isinstance(result, list)


def test_target_file_not_empty(target_file, gwt_models):
    text = Path(target_file).read_text(encoding="utf-8")
    parser = GwtParser(text, gwt_models)
    result = parser.parse()
    assert isinstance(result, list)
    assert result, "expected at least one parsed item"
