import pytest

from ..decoding import decode_indexed
from ..decoding import decode_to_list


def test_decode_to_list():
    l = decode_to_list('a☃b'.encode('utf-8'))  # noqa
    assert l == ['a', '', '', '☃', 'b']

    with pytest.raises(UnicodeDecodeError):
        decode_to_list('☃'.encode('utf-8')[:2])  # noqa


def test_decode_indexed():
    s, dsi = decode_indexed('a☃b'.encode('utf-8'))  # noqa
    assert s == 'a☃b'
    assert list(dsi.byte_offsets) == [0, 1, 4, 5]
