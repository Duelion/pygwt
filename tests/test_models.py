from pygwt import models


def test_long_value_is_int():
    """The ``Long`` wrapper should expose an integer ``value``."""

    long = models.Long(raw="xV3")  # arbitrary base64 number
    assert isinstance(long.value, int)

