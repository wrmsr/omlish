import codecs
import io
import typing as ta

from omlish import check
from omlish import lang
from omlish.formats.json.stream.building import JsonValueBuilder
from omlish.formats.json.stream.lexing import JsonStreamLexer
from omlish.formats.json.stream.parsing import Event
from omlish.formats.json.stream.parsing import JsonStreamParser
from omlish.io.buffers import DelimitingBuffer

from .formats import Format


##


class EagerParser:
    def __init__(self, fmt: Format) -> None:
        super().__init__()

        self._fmt = fmt

    def parse(self, f: ta.TextIO) -> ta.Iterator[ta.Any]:
        return self._fmt.load(f)


##


class DelimitingParser:
    def __init__(
            self,
            fmt: Format,
            *,
            delimiters: ta.Iterable[int] = b'\n',
    ) -> None:
        super().__init__()

        self._fmt = fmt

        self._db = DelimitingBuffer(delimiters)

    def parse(self, b: bytes) -> ta.Iterator[ta.Any]:
        for chunk in self._db.feed(b):
            s = check.isinstance(chunk, bytes).decode('utf-8')
            v = self._fmt.load(io.StringIO(s))
            yield v


##


class StreamBuilder(lang.ExitStacked):
    _builder: JsonValueBuilder | None = None

    def _enter_contexts(self) -> None:
        self._builder = self._enter_context(JsonValueBuilder())

    def build(self, e: Event) -> ta.Iterator[ta.Any]:
        yield from check.not_none(self._builder)(e)


class StreamParser(lang.ExitStacked):
    _decoder: codecs.IncrementalDecoder
    _lex: JsonStreamLexer
    _parse: JsonStreamParser

    def _enter_contexts(self) -> None:
        self._decoder = codecs.getincrementaldecoder('utf-8')()
        self._lex = self._enter_context(JsonStreamLexer())
        self._parse = self._enter_context(JsonStreamParser())

    def parse(self, b: bytes) -> ta.Iterator[Event]:
        for s in self._decoder.decode(b, not b):
            for c in s:
                for t in self._lex(c):
                    yield from self._parse(t)
