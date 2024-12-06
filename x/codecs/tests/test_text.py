import pytest

from omlish import check
from omlish import lang

from ..text import UTF8
from ..text import TextEncodingOptions


def test_text():
    assert UTF8.new().encode('hi') == b'hi'
    assert UTF8.new(TextEncodingOptions(errors='ignore')).encode('hi') == b'hi'

    ge = lang.nextgen(check.not_none(UTF8.new_incremental)().encode_incremental())
    assert ge.send('hi') == b'hi'
    assert ge.send('') == b''
    with pytest.raises(StopIteration):
        ge.send('')

    gd = lang.nextgen(check.not_none(UTF8.new_incremental)().decode_incremental())
    assert gd.send(b'hi') == 'hi'
    assert gd.send(b'') == ''
    with pytest.raises(StopIteration):
        gd.send(b'')

    assert UTF8.new().encode('☃') == b'\xe2\x98\x83'

    gd = lang.nextgen(check.not_none(UTF8.new_incremental)().decode_incremental())
    assert gd.send(b'\xe2') is None
    assert gd.send(b'\x98') is None
    assert gd.send(b'\x83') == '☃'
    assert gd.send(b'') == ''
    with pytest.raises(StopIteration):
        gd.send(b'')
