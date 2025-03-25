import dataclasses as dc
import typing as ta

from .... import lang
from .build import JsonObjectBuilder
from .lex import JsonStreamLexer
from .parse import JsonStreamParser


##


@dc.dataclass(kw_only=True)
class JsonStreamObjectParser(lang.ExitStacked):
    include_raw: bool = False
    yield_object_lists: bool = False

    #

    _lex: JsonStreamLexer = dc.field(init=False)
    _parse: JsonStreamParser = dc.field(init=False)
    _build: JsonObjectBuilder = dc.field(init=False)

    def _enter_contexts(self) -> None:
        self._lex = JsonStreamLexer(
            include_raw=self.include_raw,
        )

        self._parse = JsonStreamParser()

        self._build = JsonObjectBuilder(
            yield_object_lists=self.yield_object_lists,
        )

    def feed(self, i: ta.Iterable[str]) -> ta.Iterator[ta.Any]:
        for c in i:
            for t in self._lex(c):
                for e in self._parse(t):
                    for v in self._build(e):  # noqa
                        yield v


def stream_parse_one_object(
        i: ta.Iterable[str],
        **kwargs: ta.Any,
) -> ta.Any:
    with JsonStreamObjectParser(**kwargs) as p:
        return next(p.feed(i))
