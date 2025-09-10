r"""
TODO:
 - gson switches
  - Strictness.LEGACY_STRICT
   - JsonReader allows the literals true, false and null to have any capitalization, for example fAlSe or NULL
   - JsonReader supports the escape sequence \', representing a ' (single-quote)
   - JsonReader supports the escape sequence \LF (with LF being the Unicode character U+000A), resulting in a LF within
     the read JSON string
   - JsonReader allows unescaped control characters (U+0000 through U+001F)
  - Strictness.LENIENT
   - In lenient mode, all input that is accepted in legacy strict mode is accepted in addition to the following
     departures from RFC 8259:
   - Streams that start with the non-execute prefix, ")]'\n"}
   - Streams that include multiple top-level values. With legacy strict or strict parsing, each stream must contain
     exactly one top-level value.
   - Numbers may be NaNs or infinities represented by NaN and (-)Infinity respectively.
   - End of line comments starting with // or # and ending with a newline character.
   - C-style comments starting with /* and ending with */. Such comments may not be nested.
   - Names that are unquoted or 'single quoted'.
   - Strings that are unquoted or 'single quoted'.
   - Array elements separated by ; instead of ,.
   - Unnecessary array separators. These are interpreted as if null was the omitted value.
   - Names and values separated by = or => instead of :.
   - Name/value pairs separated by ; instead of ,.
"""
import dataclasses as dc
import itertools
import typing as ta

from .... import lang
from .building import JsonValueBuilder
from .lexing import JsonStreamLexer
from .parsing import JsonStreamParser


##


@dc.dataclass(kw_only=True)
class JsonStreamValueParser(lang.ExitStacked):
    include_raw: bool = False
    yield_object_lists: bool = False

    json5: bool = False

    #

    _lex: JsonStreamLexer = dc.field(init=False)
    _parse: JsonStreamParser = dc.field(init=False)
    _build: JsonValueBuilder = dc.field(init=False)

    def _enter_contexts(self) -> None:
        self._lex = JsonStreamLexer(
            include_raw=self.include_raw,
            allow_comments=self.json5,
            allow_single_quotes=self.json5,
        )

        self._parse = JsonStreamParser()

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
