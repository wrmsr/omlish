# ruff: noqa: B017 PT011
import pytest

from ..text import ConcatFacadeText
from ..text import FacadeText
from ..text import FacadeTextStyle
from ..text import StrFacadeText
from ..text import StyleFacadeText


def assert_no_concat_children(t: FacadeText) -> None:
    if isinstance(t, ConcatFacadeText):
        for c in t.l:
            assert not isinstance(c, ConcatFacadeText)
            assert_no_concat_children(c)

    elif isinstance(t, StyleFacadeText):
        assert_no_concat_children(t.c)


def assert_no_empty_concat_children(t: FacadeText) -> None:
    if isinstance(t, ConcatFacadeText):
        assert t.l
        for c in t.l:
            assert bool(c)
            assert_no_empty_concat_children(c)

    elif isinstance(t, StyleFacadeText):
        assert_no_empty_concat_children(t.c)


def assert_no_adjacent_str_children(t: FacadeText) -> None:
    if isinstance(t, ConcatFacadeText):
        last_was_str = False
        for c in t.l:
            is_str = isinstance(c, StrFacadeText)
            assert not (last_was_str and is_str)
            last_was_str = is_str
            assert_no_adjacent_str_children(c)

    elif isinstance(t, StyleFacadeText):
        assert_no_adjacent_str_children(t.c)


def assert_canonical(t: FacadeText) -> None:
    assert_no_concat_children(t)
    assert_no_empty_concat_children(t)
    assert_no_adjacent_str_children(t)


def test_blank_is_singleton() -> None:
    assert FacadeText.blank() is FacadeText.of()
    assert FacadeText.of('') is FacadeText.blank()
    assert FacadeText.of('', [], (), ['', []]) is FacadeText.blank()


def test_single_facade_text_is_returned_as_is() -> None:
    s = StrFacadeText('abc')

    assert FacadeText.of(s) is s


def test_plain_strings_are_merged() -> None:
    t = FacadeText.of('a', 'b', '', 'c')

    assert isinstance(t, StrFacadeText)
    assert t.s == 'abc'
    assert str(t) == 'abc'
    assert_canonical(t)


def test_nested_sequences_are_flattened_without_concat_when_all_strings() -> None:
    t = FacadeText.of(['a', ['b', ('c', ['', 'd'])]], 'e')

    assert isinstance(t, StrFacadeText)
    assert t.s == 'abcde'
    assert str(t) == 'abcde'
    assert_canonical(t)


def test_existing_concat_is_flattened() -> None:
    styled = StyleFacadeText(
        StrFacadeText('c'),
        FacadeTextStyle(color='red'),
    )

    inner = ConcatFacadeText((
        StrFacadeText('b'),
        styled,
        StrFacadeText('d'),
    ))

    t = FacadeText.of('a', inner, 'e')

    assert isinstance(t, ConcatFacadeText)
    assert list(t.l) == [
        StrFacadeText('ab'),
        styled,
        StrFacadeText('de'),
    ]

    assert str(t) == 'abcde'
    assert_canonical(t)


def test_adjacent_strs_are_merged_across_sequence_boundaries() -> None:
    t = FacadeText.of(
        'a',
        ['b', ['c']],
        ('d',),
        ['e'],
    )

    assert isinstance(t, StrFacadeText)
    assert t.s == 'abcde'
    assert_canonical(t)


def test_style_is_preserved_as_boundary() -> None:
    styled = StyleFacadeText(
        StrFacadeText('b'),
        FacadeTextStyle(color='green', bold=True),
    )

    t = FacadeText.of('a', styled, 'c')

    assert isinstance(t, ConcatFacadeText)
    assert list(t.l) == [
        StrFacadeText('a'),
        styled,
        StrFacadeText('c'),
    ]

    assert str(t) == 'abc'
    assert_canonical(t)


def test_adjacent_strings_on_both_sides_of_style_do_not_merge_across_style() -> None:
    styled = StyleFacadeText(
        StrFacadeText('X'),
        FacadeTextStyle(italic=True),
    )

    t = FacadeText.of(['a', 'b'], styled, ['c', 'd'])

    assert isinstance(t, ConcatFacadeText)
    assert list(t.l) == [
        StrFacadeText('ab'),
        styled,
        StrFacadeText('cd'),
    ]

    assert str(t) == 'abXcd'
    assert_canonical(t)


def test_empty_strings_and_empty_sequences_are_removed_around_style() -> None:
    styled = StyleFacadeText(
        StrFacadeText('x'),
        FacadeTextStyle(color='blue'),
    )

    t = FacadeText.of('', [], ['', styled, ''], (), '')

    assert t is styled
    assert str(t) == 'x'
    assert_canonical(t)


def test_str_of_fast_path_for_plain_string() -> None:
    assert FacadeText.str_of('abc') == 'abc'


def test_str_of_coerces_nested_facade_text() -> None:
    styled = StyleFacadeText(
        StrFacadeText('b'),
        FacadeTextStyle(color='yellow'),
    )

    assert FacadeText.str_of(['a', styled, 'c']) == 'abc'


def test_join_with_empty_delimiter() -> None:
    t = FacadeText.of('').join(['a', ['b'], 'c'])

    assert isinstance(t, StrFacadeText)
    assert t.s == 'abc'
    assert_canonical(t)


def test_join_with_string_delimiter() -> None:
    t = FacadeText.of(', ').join(['a', 'b', 'c'])

    assert isinstance(t, StrFacadeText)
    assert t.s == 'a, b, c'
    assert str(t) == 'a, b, c'
    assert_canonical(t)


def test_join_with_styled_delimiter_preserves_boundaries() -> None:
    delim = StyleFacadeText(
        StrFacadeText('|'),
        FacadeTextStyle(color='red'),
    )

    t = delim.join(['a', 'b', 'c'])

    assert isinstance(t, ConcatFacadeText)
    assert list(t.l) == [
        StrFacadeText('a'),
        delim,
        StrFacadeText('b'),
        delim,
        StrFacadeText('c'),
    ]

    assert str(t) == 'a|b|c'
    assert_canonical(t)


def test_style_with_no_attrs_is_noop() -> None:
    t = FacadeText.of('abc')

    assert t.style() is t


def test_style_of_blank_is_blank() -> None:
    assert FacadeText.of('').style(color='red') is FacadeText.blank()


def test_style_with_attrs_wraps_once() -> None:
    t = FacadeText.of('abc').style(color='red', bold=True)

    assert isinstance(t, StyleFacadeText)
    assert t.c == StrFacadeText('abc')
    assert t.y == FacadeTextStyle(color='red', bold=True)
    assert str(t) == 'abc'
    assert_canonical(t)


def test_concat_rejects_empty_children() -> None:
    with pytest.raises(Exception):
        ConcatFacadeText((StrFacadeText('a'), StrFacadeText('')))


def test_concat_rejects_nested_concat_children() -> None:
    inner = ConcatFacadeText((
        StrFacadeText('a'),
        StyleFacadeText(StrFacadeText('b')),
    ))

    with pytest.raises(Exception):
        ConcatFacadeText((inner, StrFacadeText('c')))


def test_concat_rejects_adjacent_str_children() -> None:
    with pytest.raises(Exception):
        ConcatFacadeText((StrFacadeText('a'), StrFacadeText('b')))


def test_deeply_nested_sequence_does_not_recurse() -> None:
    obj = 'x'
    for _ in range(10_000):
        obj = [obj]  # type: ignore

    t = FacadeText.of(obj)

    assert isinstance(t, StrFacadeText)
    assert t.s == 'x'
    assert_canonical(t)


def test_many_nested_singletons_with_strings_are_linearish() -> None:
    objs = []
    for i in range(1_000):
        objs.append([str(i), ['-']])

    t = FacadeText.of(*objs)

    assert isinstance(t, StrFacadeText)
    assert t.s == ''.join(f'{i}-' for i in range(1_000))
    assert_canonical(t)
