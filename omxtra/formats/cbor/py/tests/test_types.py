import pytest

from ..types import CBOR_BREAK_MARKER
from ..types import CBOR_UNDEFINED
from ..types import CborFrozenDict
from ..types import CborSimpleValue
from ..types import CborTag


def test_undefined_bool():
    assert not CBOR_UNDEFINED


def test_undefined_repr():
    assert repr(CBOR_UNDEFINED) == 'undefined'


def test_undefined_singleton():
    assert type(CBOR_UNDEFINED)() is CBOR_UNDEFINED


def test_undefined_init():
    with pytest.raises(TypeError):
        type(CBOR_UNDEFINED)('foo')  # type: ignore


def test_break_bool():
    assert CBOR_BREAK_MARKER


def test_break_repr():
    assert repr(CBOR_BREAK_MARKER) == 'break_marker'


def test_break_singleton():
    assert type(CBOR_BREAK_MARKER)() is CBOR_BREAK_MARKER


def test_break_init():
    with pytest.raises(TypeError):
        type(CBOR_BREAK_MARKER)('foo')  # type: ignore


def test_tag_init():
    with pytest.raises(TypeError):
        CborTag('foo', 'bar')


def test_tag_attr():
    tag = CborTag(1, 'foo')
    assert tag.tag == 1
    assert tag.value == 'foo'


def test_tag_compare():
    tag1 = CborTag(1, 'foo')
    tag2 = CborTag(1, 'foo')
    tag3 = CborTag(2, 'bar')
    tag4 = CborTag(2, 'baz')
    assert tag1 is not tag2
    assert tag1 == tag2
    assert not (tag1 == tag3)  # noqa
    assert tag1 != tag3
    assert tag3 >= tag2
    assert tag3 > tag2
    assert tag2 < tag3
    assert tag2 <= tag3
    assert tag4 >= tag3
    assert tag4 > tag3
    assert tag3 < tag4
    assert tag3 <= tag4


def test_tag_compare_unimplemented():
    tag = CborTag(1, 'foo')
    assert not (tag == (1, 'foo'))  # noqa
    with pytest.raises(TypeError):
        tag <= (1, 'foo')  # noqa


def test_tag_recursive_repr():
    tag = CborTag(1, None)
    tag.value = tag
    assert repr(tag) == 'CBORTag(1, ...)'
    assert tag is tag.value
    assert tag == tag.value
    assert not (tag != tag.value)  # noqa


def test_tag_recursive_hash():
    tag = CborTag(1, None)
    tag.value = tag
    with pytest.raises(RuntimeError, match='This CBORTag is not hashable'):
        hash(tag)


def test_tag_repr():
    assert repr(CborTag(600, 'blah')) == "CBORTag(600, 'blah')"


def test_simple_value_repr():
    assert repr(CborSimpleValue(1)) == 'CBORSimpleValue(value=1)'


def test_simple_value_equals():
    tag1 = CborSimpleValue(1)
    tag2 = CborSimpleValue(1)
    tag3 = CborSimpleValue(21)
    tag4 = CborSimpleValue(99)
    assert tag1 == tag2
    assert tag1 == 1
    assert not (tag2 == '21')  # noqa
    assert tag1 != tag3
    assert tag1 != 21
    assert tag2 != '21'
    assert tag4 > tag1
    assert tag4 >= tag3
    assert 99 <= tag4
    assert 100 > tag4
    assert tag4 <= 100
    assert 2 < tag4
    assert tag4 >= 99
    assert tag1 <= tag4


def test_simple_ordering():
    randints = [9, 7, 3, 8, 4, 0, 2, 5, 6, 1]
    expected = [CborSimpleValue(v) for v in range(10)]
    disordered = [CborSimpleValue(v) for v in randints]
    assert expected == sorted(disordered)
    assert expected == sorted(randints)


@pytest.mark.parametrize('value', [-1, 24, 31, 256])
def test_simple_value_out_of_range(value):
    with pytest.raises(TypeError) as exc:
        CborSimpleValue(value)

    assert str(exc.value) == 'simple value out of range (0..23, 32..255)'


def test_frozendict():
    assert len(CborFrozenDict({1: 2, 3: 4})) == 2
    assert repr(CborFrozenDict({1: 2})) == 'FrozenDict({1: 2})'
