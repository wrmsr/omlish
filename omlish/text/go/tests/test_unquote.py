# ruff: noqa: Q000
import pytest

from ..unquote import UnquoteError
from ..unquote import unquote


def test_unquote():
    for ins, out in [
        ('""', ""),
        ('"a"', "a"),
        ('"abc"', "abc"),
        ('"☺"', "☺"),
        ('"hello world"', "hello world"),
        (r'"\xFF"', "\xFF"),
        (r'"\377"', "\377"),
        (r'"\u1234"', "\u1234"),
        (r'"\U00010111"', "\U00010111"),
        (r'"\U0001011111"', "\U0001011111"),
        (r'"\a\b\f\n\r\t\v\\\""', "\a\b\f\n\r\t\v\\\""),
        ('"\'"', "'"),

        ("'a'", "a"),
        ("'☹'", "☹"),
        (r"'\a'", "\a"),
        (r"'\x10'", "\x10"),
        (r"'\377'", "\377"),
        (r"'\u1234'", "\u1234"),
        (r"'\U00010111'", "\U00010111"),
        (r"'\t'", "\t"),
        ("' '", " "),
        (r"'\''", "'"),
        ("'\"'", "\""),

        ("``", ''),
        ("`a`", 'a'),
        ("`abc`", 'abc'),
        ("`☺`", '☺'),
        ("`hello world`", 'hello world'),
        ("`\\xFF`", r'\xFF'),
        ("`\\377`", r'\377'),
        ("`\\`", '\\'),
        ("`\n`", "\n"),
        ("`	`", '\t'),
        ("` `", ' '),
        ("`a\rb`", "ab"),
    ]:
        assert unquote(ins) == out

    for out, ins in [
        ("\a\b\f\r\n\t\v", r'"\a\b\f\r\n\t\v"'),
        ("\\", r'"\\"'),
        ("abc\xffdef", r'"abc\xffdef"'),
        ("\u263a", '"☺"'),
        ("\U0010ffff", r'"\U0010ffff"'),
        ("\x04", r'"\x04"'),
        # Some non-printable but graphic runes. Final column is double-quoted.
        ("!\u00a0!\u2000!\u3000!", r'"!\u00a0!\u2000!\u3000!"'),
        ("\x7f", r'"\x7f"'),
    ]:
        assert unquote(ins) == out

    for ins in [
        '',
        '"',
        '"a',
        """"'""",
        'b"',
        r'"\"',
        r'"\9"',
        r'"\19"',
        r'"\129"',
        r"'\'",
        r"'\9'",
        r"'\19'",
        r"'\129'",
        "'ab'",
        r'"\x1!"',
        r'"\U12345678"',
        r'"\z"',
        "`",
        "`xxx",
        "``x\r",
        "`\"",
        # r""""\'""""",  # FIXME: ruff parser bug lol
        '"\\\'',
        r"""'\"'""",
        "\"\n\"",
        "\"\\n\n\"",
        "'\n'",
        r'"\udead"',
        r'"\ud83d\ude4f"',
    ]:
        with pytest.raises(UnquoteError):
            unquote(ins)
