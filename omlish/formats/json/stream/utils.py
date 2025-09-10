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
import abc
import itertools
import typing as ta

from .... import lang
from .building import JsonValueBuilder
from .errors import JsonStreamError
from .lexing import JsonStreamLexer
from .parsing import JsonStreamParser


##


class AbstractJsonStreamValueParser(lang.ExitStacked, lang.Abstract):
    _lex: JsonStreamLexer
    _parse: JsonStreamParser
    _build: JsonValueBuilder

    @abc.abstractmethod
    def _make(self) -> tuple[
        JsonStreamLexer,
        JsonStreamParser,
        JsonValueBuilder,
    ]:
        raise NotImplementedError

    #

    def _enter_contexts(self) -> None:
        self._lex, self._parse, self._build = self._make()

    def feed(self, i: ta.Iterable[str]) -> ta.Iterator[ta.Any]:
        for c in i:
            for t in self._lex(c):
                for e in self._parse(t):
                    for v in self._build(e):  # noqa
                        yield v

    #

    @classmethod
    def parse_values(
            cls,
            i: ta.Iterable[str],
            **kwargs: ta.Any,
    ) -> ta.Generator[ta.Any]:
        with cls(**kwargs) as p:
            yield from p.feed(itertools.chain(i, ['']))

    @classmethod
    def parse_one_value(
            cls,
            i: ta.Iterable[str],
            **kwargs: ta.Any,
    ) -> ta.Any:
        with cls(**kwargs) as p:
            return next(p.feed(itertools.chain(i, [''])))

    @classmethod
    def parse_exactly_one_value(
            cls,
            i: ta.Iterable[str],
            **kwargs: ta.Any,
    ) -> ta.Any:
        r: ta.Any
        r = not_set = object()
        with cls(**kwargs) as p:
            for v in p.feed(itertools.chain(i, [''])):
                if r is not_set:
                    r = v
                else:
                    raise JsonStreamError('Unexpected input')
        if r is not_set:
            raise JsonStreamError('No value')
        return r


##


class JsonStreamValueParser(AbstractJsonStreamValueParser):
    def __init__(
            self,
            *,
            include_raw: bool = False,
            yield_object_lists: bool = False,
    ) -> None:
        super().__init__()

        self._include_raw = include_raw
        self._yield_object_lists = yield_object_lists

    def _make(self) -> tuple[
        JsonStreamLexer,
        JsonStreamParser,
        JsonValueBuilder,
    ]:
        return (
            JsonStreamLexer(
                include_raw=self._include_raw,
            ),

            JsonStreamParser(),

            JsonValueBuilder(
                yield_object_lists=self._yield_object_lists,
            ),
        )


stream_parse_values = JsonStreamValueParser.parse_values
stream_parse_one_value = JsonStreamValueParser.parse_one_value
stream_parse_exactly_one_value = JsonStreamValueParser.parse_exactly_one_value
