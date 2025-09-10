"""
TODO:

Objects:
 - Object keys may be an ECMAScript 5.1 IdentifierName.
 + Objects may have a single trailing comma.
Arrays:
 + Arrays may have a single trailing comma.
Strings:
 + Strings may be single quoted.
 + Strings may span multiple lines by escaping new line characters.
 + Strings may include character escapes.
Numbers:
 + Numbers may be hexadecimal.
 + Numbers may have a leading or trailing decimal point.
 + Numbers may be IEEE 754 positive infinity, negative infinity, and NaN.
 + Numbers may begin with an explicit plus sign.
Comments:
 + Single and multi-line comments are allowed.
White Space:
 - Additional white space characters are allowed.
"""
import dataclasses as dc
import itertools
import typing as ta

from ... import lang
from ..json.stream.building import JsonValueBuilder
from ..json.stream.lexing import JsonStreamLexer
from ..json.stream.parsing import JsonStreamParser
from .literals import parse_number_literal
from .literals import parse_string_literal


##


@dc.dataclass(kw_only=True)
class JsonStreamValueParser(lang.ExitStacked):
    include_raw: bool = False
    yield_object_lists: bool = False

    #

    _lex: JsonStreamLexer = dc.field(init=False)
    _parse: JsonStreamParser = dc.field(init=False)
    _build: JsonValueBuilder = dc.field(init=False)

    def _enter_contexts(self) -> None:
        self._lex = JsonStreamLexer(
            include_raw=self.include_raw,

            allow_comments=True,
            allow_single_quotes=True,

            string_literal_parser=parse_string_literal,

            allow_extended_number_literals=True,
            number_literal_parser=parse_number_literal,

            allow_extended_identifiers=True,
        )

        self._parse = JsonStreamParser(
            allow_trailing_commas=True,
        )

        self._build = JsonValueBuilder(
            yield_object_lists=self.yield_object_lists,
        )

    def feed(self, i: ta.Iterable[str]) -> ta.Iterator[ta.Any]:
        for c in itertools.chain(i, ['']):
            for t in self._lex(c):
                for e in self._parse(t):
                    for v in self._build(e):  # noqa
                        yield v


def stream_parse_values(
        i: ta.Iterable[str],
        **kwargs: ta.Any,
) -> ta.Generator[ta.Any]:
    with JsonStreamValueParser(**kwargs) as p:
        yield from p.feed(i)


def stream_parse_one_value(
        i: ta.Iterable[str],
        **kwargs: ta.Any,
) -> ta.Any:
    with JsonStreamValueParser(**kwargs) as p:
        return next(p.feed(i))
