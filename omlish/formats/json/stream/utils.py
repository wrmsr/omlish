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
import itertools
import typing as ta

from .... import lang
from .building import JsonValueBuilder
from .errors import JsonStreamError
from .lexing import JsonStreamLexer
from .lexing import Token
from .parsing import Event
from .parsing import JsonStreamParser


##


class JsonStreamValueParser(lang.ExitStacked):
    class Machinery(ta.NamedTuple):
        lex: JsonStreamLexer
        parse: JsonStreamParser
        build: JsonValueBuilder

    def __init__(self, m: Machinery) -> None:
        super().__init__()

        self._m = m

    #

    def _enter_contexts(self) -> None:
        self._enter_context(self._m.lex)
        self._enter_context(self._m.parse)

    def feed(self, i: ta.Iterable[str]) -> ta.Iterator[ta.Any]:
        for c in i:
            for t in self._m.lex(c):
                for e in self._m.parse(t):
                    for v in self._m.build(e):  # noqa
                        yield v

    #

    @classmethod
    def parse_values(
            cls,
            m: Machinery,
            i: ta.Iterable[str],
    ) -> ta.Iterator[ta.Any]:
        with cls(m) as p:
            yield from p.feed(itertools.chain(i, ['']))

    @classmethod
    def parse_one_value(
            cls,
            m: Machinery,
            i: ta.Iterable[str],
    ) -> ta.Any:
        with cls(m) as p:
            return next(p.feed(itertools.chain(i, [''])))

    @classmethod
    def parse_exactly_one_value(
            cls,
            m: Machinery,
            i: ta.Iterable[str],
    ) -> ta.Any:
        r: ta.Any
        r = not_set = object()
        with cls(m) as p:
            for v in p.feed(itertools.chain(i, [''])):
                if r is not_set:
                    r = v
                else:
                    raise JsonStreamError('Unexpected input')
        if r is not_set:
            raise JsonStreamError('No value')
        return r


##


class DebugJsonStreamValueParser(JsonStreamValueParser):
    def __init__(self, m: JsonStreamValueParser.Machinery) -> None:
        super().__init__(m)

        self._chars: list[str] = []
        self._tokens: list[Token] = []
        self._events: list[Event] = []
        self._values: list[ta.Any] = []

    def feed(self, i: ta.Iterable[str]) -> ta.Iterator[ta.Any]:
        for c in i:
            self._chars.append(c)
            for t in self._m.lex(c):
                self._tokens.append(t)
                for e in self._m.parse(t):
                    self._events.append(e)
                    for v in self._m.build(e):
                        self._values.append(v)
                        yield v


##


def make_machinery(
        *,
        include_raw: bool = False,
        yield_object_lists: bool = False,
) -> JsonStreamValueParser.Machinery:
    return JsonStreamValueParser.Machinery(
        JsonStreamLexer(
            include_raw=include_raw,
        ),

        JsonStreamParser(),

        JsonValueBuilder(
            yield_object_lists=yield_object_lists,
        ),
    )


def stream_parse_values(i: ta.Iterable[str], **kwargs: ta.Any) -> ta.Iterator[ta.Any]:
    return JsonStreamValueParser.parse_values(make_machinery(**kwargs), i)


def stream_parse_one_value(i: ta.Iterable[str], **kwargs: ta.Any) -> ta.Any:
    return JsonStreamValueParser.parse_one_value(make_machinery(**kwargs), i)


def stream_parse_exactly_one_value(i: ta.Iterable[str], **kwargs: ta.Any) -> ta.Any:
    return JsonStreamValueParser.parse_exactly_one_value(make_machinery(**kwargs), i)
