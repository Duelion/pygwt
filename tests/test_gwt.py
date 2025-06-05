import pytest

from pygwt.parser import GwtParser
from pygwt.gwt_codes import Rfi, SifmConsulta


def test_get_codes():
    rfi = Rfi()
    gwt_permutation = rfi.get_gwt_permutation()
    gwt_strong_name = rfi.get_strong_name()
    sifm_consulta = SifmConsulta()
    sifm_permutation = sifm_consulta.get_gwt_permutation()
    sifm_strong_name = sifm_consulta.get_strong_name()
    print(1)

def test_gwt(gwt_file, gwt_models):
    text = gwt_file.read_text()
    parser = GwtParser(text, gwt_models)
    result = parser.parse()
    print()

def test_gwt(gwt_file, gwt_models):
    text = gwt_file.read_text()
    parser = GwtParser(text, gwt_models)
    result = parser.parse()
    print()

def test_target_gwt(target_file, gwt_models):
    text = target_file.read_text()
    parser = GwtParser(text, gwt_models)
    result = parser.parse()
    print()