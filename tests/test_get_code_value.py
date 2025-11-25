from pygwt.parser import GwtParser


def _make_parser():
    """Create a ``GwtParser`` with a minimal table for ``get_code_value`` tests."""

    # Response with a single table entry ``"foo"`` and a single code ``1``.
    text = "//OK[1,[\"foo\"],0,7]"
    return GwtParser(text)


def test_get_code_value_basic_cases():
    parser = _make_parser()

    # index into the table (1-based)
    assert parser.get_code_value(1) == "foo"
    # zero maps to ``None``
    assert parser.get_code_value(0) is None
    # literal strings are returned as-is
    assert parser.get_code_value("bar") == "bar"
    # codes greater than the table size are returned unchanged
    assert parser.get_code_value(99) == 99


def test_get_code_value_history_lookup():
    parser = _make_parser()
    parser.history.append("prev")
    assert parser.get_code_value(-1) == "prev"

