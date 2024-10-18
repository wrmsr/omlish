"""
TODO:
 - end-of-line   = ( cr lf / cr / lf )
"""
import string
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


class SseDecoderOutput(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class SseComment(SseDecoderOutput, lang.Final):
    data: bytes


SseEventId: ta.TypeAlias = bytes


@dc.dataclass(frozen=True)
class SseEvent(SseDecoderOutput, lang.Final):
    type: bytes
    data: bytes
    last_id: SseEventId | None = None


_DIGIT_BYTES = string.digits.encode('ascii')


class SseDecoder:
    """https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation"""

    def __init__(self) -> None:
        super().__init__()

        self._event_type: bytes | None = None
        self._data: list[bytes] = []
        self._last_event_id: bytes | None = None
        self._reconnection_time: int | None = None

    def _reset(self) -> None:
        self._event_type = None
        self._data = []

    def _process_field(self, name: bytes, value: bytes) -> None:
        if name == b'event':
            self._event_type = value

        elif name == b'data':
            self._data.append(value)
            self._data.append(b'\n')

        elif name == b'id':
            if 0 not in value:
                self._last_event_id = value

        elif name == b'retry':
            if all(c in _DIGIT_BYTES for c in value):
                self._reconnection_time = int(value)

    def _dispatch_event(self) -> SseEvent:
        if self._data:
            data = b''.join([
                *(self._data[:-1] if len(self._data) > 1 else []),
                (last[:-1] if (last := self._data[-1]).endswith(b'\n') else last),
            ])
        else:
            data = b''

        e = SseEvent(
            type=self._event_type,
            data=data,
            last_id=self._last_event_id,
        )

        self._reset()

        return e

    def process_line(self, line: bytes) -> ta.Iterable[SseDecoderOutput]:
        if not line:
            yield self._dispatch_event()

        elif line[0] == b':':
            yield SseComment(line)

        elif (c := line.find(b':')) >= 0:
            if len(line) > c + 1 and line[c] == b' ':
                c += 1
            self._process_field(line[:c], line[c + 1:])

        else:
            self._process_field(line, b'')


TESTS = [
    [
        b'data: YHOO',
        b'data: +2',
        b'data: 10',
        b'',
    ],
    [
        b': test stream',
        b'',
        b'data: first event',
        b'id: 1',
        b'',
        b'data:second event',
        b'id',
        b'',
        b'data:  third event',
    ],
    [
        b'data',
        b'',
        b'data ',
        b'data ',
        b'',
        b'data:',
    ],
    [
        b': test stream',
        b'',
        b'data: first event',
        b'id: 1',
        b'',
        b'data:second event',
        b'id',
        b'',
        b'data:  third event',
    ],
    [
        b'data',
        b'',
        b'data',
        b'data',
        b'',
        b'data:',
    ],
    [
        b'data:test',
        b'',
        b'data: test',
        b'',
    ],
]


def _main() -> None:
    for test in TESTS:
        dec = SseDecoder()
        for line in test:
            for event in dec.process_line(line):
                print(event)
        print()


if __name__ == '__main__':
    _main()
