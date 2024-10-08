import pytest

from ..exceptions import ProtocolError
from ..utils import validate_nickname


@pytest.mark.parametrize('name', [
    b'a',
    b'[]\\_^{|}-',
    b'nick1',
])
def test_validate_nickname(name):
    validate_nickname(name)


@pytest.mark.parametrize('name', [
    b'',
    b'toolongggg',
    b'1nick',
    b'\x00nick',
    b'nick name',
], ids=['empty', 'toolong', 'starts_with_number', 'starts_with_nul', 'space'])
def test_validate_nickname_invalid(name):
    exc = pytest.raises(ProtocolError, validate_nickname, name)
    assert str(exc.value) == (f'IRC protocol violation: invalid nickname: {name.decode("ascii", errors="backslashreplace")}')  # noqa
