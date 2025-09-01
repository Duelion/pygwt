import pytest

from pygwt.utils import encoder, decoder


def test_encoder_decoder_roundtrip():
    numbers = [0, 1, 64, 12345, 987654321]
    for number in numbers:
        assert decoder(encoder(number)) == number


def test_encoder_negative():
    with pytest.raises(ValueError):
        encoder(-1)


def test_decoder_invalid_char():
    with pytest.raises(ValueError):
        decoder("abc!")


def test_decoder_empty_string():
    with pytest.raises(ValueError):
        decoder("")
