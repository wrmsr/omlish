import pytest

from ..strings import is_dunder
from ..strings import is_sunder
from ..strings import must_remove_prefix
from ..strings import must_remove_suffix


def test_is_dunder():
    assert is_dunder('__foo__')
    assert not is_dunder('__foo')
    assert not is_dunder('foo__')
    assert not is_dunder('_foo_')
    assert not is_dunder('____')
    assert not is_dunder('')


def test_is_sunder():
    assert is_sunder('_foo_')
    assert not is_sunder('__foo__')
    assert not is_sunder('_foo')
    assert not is_sunder('foo_')
    assert not is_sunder('_')
    assert not is_sunder('__')
    assert not is_sunder('')


def test_must_remove_prefix():
    assert must_remove_prefix('abc', 'ab') == 'c'
    assert must_remove_prefix('abc', '') == 'abc'
    assert must_remove_prefix(b'abc', b'ab') == b'c'
    with pytest.raises(ValueError):  # noqa
        must_remove_prefix('abc', 'x')


def test_must_remove_suffix():
    assert must_remove_suffix('abc', 'bc') == 'a'
    assert must_remove_suffix('abc', '') == 'abc'
    assert must_remove_suffix(b'abc', b'bc') == b'a'
    assert must_remove_suffix(b'abc', b'') == b'abc'
    with pytest.raises(ValueError):  # noqa
        must_remove_suffix('abc', 'x')
