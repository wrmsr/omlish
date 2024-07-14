import pytest

from .. import varint


def test_varint():
    b = varint.encode(420)
    assert isinstance(b, bytes)
    i = varint.decode(b)
    assert i == 420
    with pytest.raises(ValueError):
        varint.encode(-420)
