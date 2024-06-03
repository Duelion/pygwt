import pytest

from pygwt.parser import GwtParser


def test_gwt(f29_gwt_text, gwt_models):
    parser = GwtParser(f29_gwt_text, gwt_models)
    result = parser.parse()
    print()

