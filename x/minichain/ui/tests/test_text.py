# ruff: noqa: B017 PT011
import pytest

from omcore import marshal as msh

from ..text import ConcatUiText
from ..text import StrUiText
from ..text import StyleUiText
from ..text import UiText
from ..text import UiTextStyle


def assert_no_concat_children(t: UiText) -> None:
    if isinstance(t, ConcatUiText):
        for c in t.l:
            assert not isinstance(c, ConcatUiText)
            assert_no_concat_children(c)

    elif isinstance(t, StyleUiText):
        assert_no_concat_children(t.c)


def assert_no_empty_concat_children(t: UiText) -> None:
    if isinstance(t, ConcatUiText):
        assert t.l
        for c in t.l:
            assert bool(c)
            assert_no_empty_concat_children(c)

    elif isinstance(t, StyleUiText):
        assert_no_empty_concat_children(t.c)


def assert_no_adjacent_str_children(t: UiText) -> None:
    if isinstance(t, ConcatUiText):
        last_was_str = False
        for c in t.l:
            is_str = isinstance(c, StrUiText)
            assert not (last_was_str and is_str)
            last_was_str = is_str
            assert_no_adjacent_str_children(c)

    elif isinstance(t, StyleUiText):
        assert_no_adjacent_str_children(t.c)


def assert_canonical(t: UiText) -> None:
    assert_no_concat_children(t)
    assert_no_empty_concat_children(t)
    assert_no_adjacent_str_children(t)


def test_blank_is_singleton() -> None:
    assert UiText.blank() is UiText.of()
    assert UiText.of('') is UiText.blank()
    assert UiText.of('', [], (), ['', []]) is UiText.blank()


def test_single_ui_text_is_returned_as_is() -> None:
    s = StrUiText('abc')

    assert UiText.of(s) is s


def test_plain_strings_are_merged() -> None:
    t = UiText.of('a', 'b', '', 'c')

    assert isinstance(t, StrUiText)
    assert t.s == 'abc'
    assert str(t) == 'abc'
    assert_canonical(t)


def test_nested_sequences_are_flattened_without_concat_when_all_strings() -> None:
    t = UiText.of(['a', ['b', ('c', ['', 'd'])]], 'e')

    assert isinstance(t, StrUiText)
    assert t.s == 'abcde'
    assert str(t) == 'abcde'
    assert_canonical(t)


def test_existing_concat_is_flattened() -> None:
    styled = StyleUiText(
        StrUiText('c'),
        UiTextStyle(color='red'),
    )

    inner = ConcatUiText((
        StrUiText('b'),
        styled,
        StrUiText('d'),
    ))

    t = UiText.of('a', inner, 'e')

    assert isinstance(t, ConcatUiText)
    assert list(t.l) == [
        StrUiText('ab'),
        styled,
        StrUiText('de'),
    ]

    assert str(t) == 'abcde'
    assert_canonical(t)


def test_adjacent_strs_are_merged_across_sequence_boundaries() -> None:
    t = UiText.of(
        'a',
        ['b', ['c']],
        ('d',),
        ['e'],
    )

    assert isinstance(t, StrUiText)
    assert t.s == 'abcde'
    assert_canonical(t)


def test_style_is_preserved_as_boundary() -> None:
    styled = StyleUiText(
        StrUiText('b'),
        UiTextStyle(color='green', bold=True),
    )

    t = UiText.of('a', styled, 'c')

    assert isinstance(t, ConcatUiText)
    assert list(t.l) == [
        StrUiText('a'),
        styled,
        StrUiText('c'),
    ]

    assert str(t) == 'abc'
    assert_canonical(t)


def test_adjacent_strings_on_both_sides_of_style_do_not_merge_across_style() -> None:
    styled = StyleUiText(
        StrUiText('X'),
        UiTextStyle(italic=True),
    )

    t = UiText.of(['a', 'b'], styled, ['c', 'd'])

    assert isinstance(t, ConcatUiText)
    assert list(t.l) == [
        StrUiText('ab'),
        styled,
        StrUiText('cd'),
    ]

    assert str(t) == 'abXcd'
    assert_canonical(t)


def test_empty_strings_and_empty_sequences_are_removed_around_style() -> None:
    styled = StyleUiText(
        StrUiText('x'),
        UiTextStyle(color='blue'),
    )

    t = UiText.of('', [], ['', styled, ''], (), '')

    assert t is styled
    assert str(t) == 'x'
    assert_canonical(t)


def test_str_of_fast_path_for_plain_string() -> None:
    assert UiText.str_of('abc') == 'abc'


def test_str_of_coerces_nested_ui_text() -> None:
    styled = StyleUiText(
        StrUiText('b'),
        UiTextStyle(color='yellow'),
    )

    assert UiText.str_of(['a', styled, 'c']) == 'abc'


def test_join_with_empty_delimiter() -> None:
    t = UiText.of('').join(['a', ['b'], 'c'])

    assert isinstance(t, StrUiText)
    assert t.s == 'abc'
    assert_canonical(t)


def test_join_with_string_delimiter() -> None:
    t = UiText.of(', ').join(['a', 'b', 'c'])

    assert isinstance(t, StrUiText)
    assert t.s == 'a, b, c'
    assert str(t) == 'a, b, c'
    assert_canonical(t)


def test_join_with_styled_delimiter_preserves_boundaries() -> None:
    delim = StyleUiText(
        StrUiText('|'),
        UiTextStyle(color='red'),
    )

    t = delim.join(['a', 'b', 'c'])

    assert isinstance(t, ConcatUiText)
    assert list(t.l) == [
        StrUiText('a'),
        delim,
        StrUiText('b'),
        delim,
        StrUiText('c'),
    ]

    assert str(t) == 'a|b|c'
    assert_canonical(t)


def test_style_with_no_attrs_is_noop() -> None:
    t = UiText.of('abc')

    assert t.style() is t


def test_style_of_blank_is_blank() -> None:
    assert UiText.of('').style(color='red') is UiText.blank()


def test_style_with_attrs_wraps_once() -> None:
    t = UiText.of('abc').style(color='red', bold=True)

    assert isinstance(t, StyleUiText)
    assert t.c == StrUiText('abc')
    assert t.y == UiTextStyle(color='red', bold=True)
    assert str(t) == 'abc'
    assert_canonical(t)


def test_concat_rejects_empty_children() -> None:
    with pytest.raises(Exception):
        ConcatUiText((StrUiText('a'), StrUiText('')))


def test_concat_rejects_nested_concat_children() -> None:
    inner = ConcatUiText((
        StrUiText('a'),
        StyleUiText(StrUiText('b')),
    ))

    with pytest.raises(Exception):
        ConcatUiText((inner, StrUiText('c')))


def test_concat_rejects_adjacent_str_children() -> None:
    with pytest.raises(Exception):
        ConcatUiText((StrUiText('a'), StrUiText('b')))


def test_deeply_nested_sequence_does_not_recurse() -> None:
    obj = 'x'
    for _ in range(10_000):
        obj = [obj]  # type: ignore

    t = UiText.of(obj)

    assert isinstance(t, StrUiText)
    assert t.s == 'x'
    assert_canonical(t)


def test_many_nested_singletons_with_strings_are_linearish() -> None:
    objs = []
    for i in range(1_000):
        objs.append([str(i), ['-']])

    t = UiText.of(*objs)

    assert isinstance(t, StrUiText)
    assert t.s == ''.join(f'{i}-' for i in range(1_000))
    assert_canonical(t)


def test_marshal() -> None:
    tx = ConcatUiText((
        StrUiText('abc'),
        StyleUiText(
            StrUiText('def'),
            UiTextStyle(color='red'),
        ),
        StrUiText('ghi'),
    ))

    v = msh.marshal(tx, UiText)

    tx2 = msh.unmarshal(v, UiText)

    assert tx2 == tx
