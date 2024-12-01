import codecs
import io
import typing as ta

from omlish import check
from omlish import lang
from omlish.formats.json.stream.build import JsonObjectBuilder
from omlish.formats.json.stream.lex import JsonStreamLexer
from omlish.formats.json.stream.parse import JsonStreamParser
from omlish.formats.json.stream.parse import JsonStreamParserEvent
from omlish.lite.io import DelimitingBuffer

from .formats import Format


##


class EagerParser:
    def __init__(self, fmt: Format) -> None:
        super().__init__()

        self._fmt = fmt

    def parse(self, f: ta.TextIO) -> ta.Generator[ta.Any, None, None]:
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

    def parse(self, b: bytes) -> ta.Generator[ta.Any, None, None]:
        for chunk in self._db.feed(b):
            s = check.isinstance(chunk, bytes).decode('utf-8')
            v = self._fmt.load(io.StringIO(s))
            yield v


##


class StreamBuilder(lang.ExitStacked):
    _builder: JsonObjectBuilder | None = None

    def __enter__(self) -> ta.Self:
        super().__enter__()
        self._builder = self._enter_context(JsonObjectBuilder())
        return self

    def build(self, e: JsonStreamParserEvent) -> ta.Generator[ta.Any, None, None]:
        yield from check.not_none(self._builder)(e)


class StreamParser(lang.ExitStacked):
    _decoder: codecs.IncrementalDecoder
    _lex: JsonStreamLexer
    _parse: JsonStreamParser

    def __enter__(self) -> ta.Self:
        super().__enter__()
        self._decoder = codecs.getincrementaldecoder('utf-8')()
        self._lex = self._enter_context(JsonStreamLexer())
        self._parse = self._enter_context(JsonStreamParser())
        return self

    def parse(self, b: bytes) -> ta.Generator[JsonStreamParserEvent, None, None]:
        for s in self._decoder.decode(b, not b):
            for c in s:
                for t in self._lex(c):
                    yield from self._parse(t)
