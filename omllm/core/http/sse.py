import abc
import codecs
import dataclasses as dc
import io
import typing as ta

from omcore import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class SseEvent:
    event: str | None
    data: str
    raw: ta.Sequence[str]


class SseDecoder[I](lang.Abstract):
    @abc.abstractmethod
    def feed(self, chunk: I) -> ta.Iterator[SseEvent]:
        raise NotImplementedError

    @abc.abstractmethod
    def finish(self) -> ta.Iterator[SseEvent]:
        raise NotImplementedError


##


class StrSseDecoder(SseDecoder[str]):
    def __init__(self) -> None:
        super().__init__()

        self._event: str | None = None
        self._data: list[str] = []
        self._raw: list[str] = []

        # Holds at most one partial line: it never contains a '\n', and contains a '\r' only as its final character.
        # _pending_cr tracks that trailing '\r' (which might be the first half of a '\r\n' split across chunks), and is
        # always equivalent to `buffer contents end with '\r'`. This invariant is what lets _consume_lines scan only the
        # new chunk: every line break it could ever find is either the tracked pending '\r' or somewhere in the new
        # data.
        self._buf = io.StringIO()
        self._pending_cr = False

    def _flush_event(self) -> SseEvent | None:
        if self._event is None and not self._data:
            return None

        event = SseEvent(
            event=self._event,
            data='\n'.join(self._data),
            raw=tuple(self._raw),
        )
        self._event = None
        self._data = []
        self._raw = []
        return event

    def _decode_line(self, line: str) -> SseEvent | None:
        if line == '':
            return self._flush_event()

        self._raw.append(line)
        if line.startswith(':'):
            return None

        delim = line.find(':')
        field_name = line if delim == -1 else line[:delim]
        value = '' if delim == -1 else line[delim + 1:]
        value = value.removeprefix(' ')

        if field_name == 'event':
            self._event = value
        elif field_name == 'data':
            self._data.append(value)

        return None

    def _take_buf(self) -> str:
        buf = self._buf.getvalue()
        self._buf = io.StringIO()
        return buf

    def _consume_lines(self, chunk: str) -> ta.Iterator[str]:
        if not chunk:
            return

        cr = chunk.find('\r')
        nl = chunk.find('\n')

        if not self._pending_cr and cr == -1 and nl == -1:
            # No line breaks anywhere - the buffered partial line just grows. This is the hot path for pathological
            # break-free input: one amortized-O(len(chunk)) append, and nothing already buffered is ever rescanned.
            self._buf.write(chunk)
            return

        pos = 0  # Start of the current line, as an index into chunk.

        if self._pending_cr:
            # The buffered partial line ends with '\r' - now that there's more input we know whether it was a lone '\r'
            # break or the first half of a '\r\n'. Either way it terminates a line held entirely in the buffer.
            self._pending_cr = False
            if chunk[0] == '\n':
                pos = 1
            yield self._take_buf()[:-1]

        while True:
            # The buffered tail is break-free, so every remaining break lies within chunk. The cached find results can
            # only go stale by falling behind pos - never rescan already-scanned data, and a -1 stays a -1.
            if -1 < cr < pos:
                cr = chunk.find('\r', pos)
            if -1 < nl < pos:
                nl = chunk.find('\n', pos)
            if cr == -1 and nl == -1:
                break
            if cr == -1:
                brk = nl
            elif nl == -1:
                brk = cr
            else:
                brk = min(cr, nl)

            nxt = brk + 1
            if chunk[brk] == '\r':
                if nxt < len(chunk):
                    if chunk[nxt] == '\n':
                        nxt += 1
                else:
                    # A trailing '\r' might be the start of a '\r\n' split across chunks - buffer the rest and wait for
                    # more input.
                    self._buf.write(chunk[pos:])
                    self._pending_cr = True
                    return

            if pos == 0 and self._buf.tell():
                # The first line spans the buffered partial line plus the start of this chunk.
                yield self._take_buf() + chunk[:brk]
            else:
                yield chunk[pos:brk]
            pos = nxt

        if pos < len(chunk):
            self._buf.write(chunk[pos:])

    def feed(self, chunk: str) -> ta.Iterator[SseEvent]:
        for line in self._consume_lines(chunk):
            if (event := self._decode_line(line)) is not None:
                yield event

    def finish(self) -> ta.Iterator[SseEvent]:
        buf = self._take_buf()
        self._pending_cr = False

        if buf.endswith('\r'):
            if (event := self._decode_line(buf[:-1])) is not None:
                yield event
        elif buf:
            if (event := self._decode_line(buf)) is not None:
                yield event

        if (event := self._flush_event()) is not None:
            yield event


##


class Utf8SseDecoder(SseDecoder[lang.Bytes]):
    def __init__(self) -> None:
        super().__init__()

        self._utf8 = codecs.getincrementaldecoder('utf-8')(errors='replace')
        self._sse = StrSseDecoder()

    def feed(self, chunk: lang.Bytes) -> ta.Iterator[SseEvent]:
        return self._sse.feed(self._utf8.decode(chunk))  # noqa

    def finish(self) -> ta.Iterator[SseEvent]:
        yield from self._sse.feed(self._utf8.decode(b'', True))  # noqa
        yield from self._sse.finish()
