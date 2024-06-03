import pytest

from pygwt.parser import GwtParser


def test_gwt(f29_gwt_file, gwt_models):
    text = f29_gwt_file.read_text()
    parser = GwtParser(text, gwt_models)
    result = parser.parse()
    print()

