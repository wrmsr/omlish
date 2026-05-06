import re
import typing as ta

from ..re import regex_to_string


def roundtrip(rx):
    src = regex_to_string(rx)
    return src, re.compile(src)


def test_plain_str_pattern_is_returned_unchanged():
    assert regex_to_string(r'^foo$') == r'^foo$'


def test_plain_bytes_pattern_is_returned_unchanged():
    assert regex_to_string(rb'^foo$') == rb'^foo$'


def test_str_multiline_ignorecase_flags_are_inlined():
    rx = re.compile(r'^foo$', re.MULTILINE | re.IGNORECASE)

    src, rx2 = roundtrip(rx)

    assert src == r'(?im)^foo$'
    assert rx2.search('FOO\nbar')
    assert rx2.search('bar\nFOO')


def test_str_dotall_verbose_flags_are_inlined():
    rx = re.compile(
        r"""
        foo . bar
        """,
        re.DOTALL | re.VERBOSE,
    )

    src, rx2 = roundtrip(rx)

    assert src.startswith('(?sx)')
    assert rx2.search('foo\nbar')


def test_str_inline_ascii_flag_survives_via_pattern_itself():
    rx = re.compile(r'(?a)\w+')

    src, rx2 = roundtrip(rx)

    assert src == r'(?a)\w+'
    assert not rx2.match('é')


def test_str_unicode_flag_is_omitted_by_default():
    rx = re.compile(r'\w+')

    src, rx2 = roundtrip(rx)

    assert src == r'\w+'
    assert rx2.match('é')


def test_str_ascii_flag_is_preserved():
    rx = re.compile(r'\w+', re.ASCII)

    src, rx2 = roundtrip(rx)

    assert src == r'(?a)\w+'
    assert rx2.match('abc')
    assert not rx2.match('é')


def test_bytes_pattern_returns_bytes_source():
    rx = re.compile(rb'^foo$', re.MULTILINE | re.IGNORECASE)

    src, rx2 = roundtrip(rx)

    assert isinstance(src, bytes)
    assert src == rb'(?im)^foo$'
    assert rx2.search(b'FOO\nbar')
    assert rx2.search(b'bar\nFOO')


def test_bytes_ascii_flag_is_not_emitted_when_implicit():
    rx = re.compile(rb'\w+')

    src, rx2 = roundtrip(rx)

    assert src == rb'\w+'
    assert rx2.match(b'abc')
    assert not rx2.match(b'\xe9')


def test_bytes_locale_flag_is_inlined():
    rx = re.compile(rb'\w+', re.LOCALE)

    src, rx2 = roundtrip(rx)

    assert src == rb'(?L)\w+'
    assert isinstance(rx2, re.Pattern)


def test_debug_flag_is_ignored():
    rx = re.compile(r'foo', re.DEBUG)

    src = regex_to_string(rx)

    assert src == r'foo'
    assert re.compile(src).search('foo')


def test_output_is_semantically_roundtrippable_for_relevant_flags():
    cases = [
        re.compile(r'^foo$', re.MULTILINE),
        re.compile(r'foo.bar', re.DOTALL),
        re.compile(r'foo', re.IGNORECASE),
        re.compile(r'\w+', re.ASCII),
        re.compile(rb'^foo$', re.MULTILINE),
        re.compile(rb'foo.bar', re.DOTALL),
        re.compile(rb'foo', re.IGNORECASE),
    ]

    rx: ta.Any
    for rx in cases:
        src, rx2 = roundtrip(rx)

        assert type(src) is type(rx.pattern)
        assert rx2.pattern == src
        assert bool(rx2.flags & re.IGNORECASE) == bool(rx.flags & re.IGNORECASE)
        assert bool(rx2.flags & re.MULTILINE) == bool(rx.flags & re.MULTILINE)
        assert bool(rx2.flags & re.DOTALL) == bool(rx.flags & re.DOTALL)
        assert bool(rx2.flags & re.ASCII) == bool(rx.flags & re.ASCII)
