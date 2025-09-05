import dataclasses as dc
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

    allow_comments: bool = False

    #

    _lex: JsonStreamLexer = dc.field(init=False)
    _parse: JsonStreamParser = dc.field(init=False)
    _build: JsonValueBuilder = dc.field(init=False)

    def _enter_contexts(self) -> None:
        self._lex = JsonStreamLexer(
            include_raw=self.include_raw,
            allow_comments=self.allow_comments,
        )

        self._parse = JsonStreamParser()

        self._build = JsonValueBuilder(
            yield_object_lists=self.yield_object_lists,
        )

    def feed(self, i: ta.Iterable[str]) -> ta.Iterator[ta.Any]:
        for c in i:
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
