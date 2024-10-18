"""
TODO:
 - end-of-line   = ( cr lf / cr / lf )
"""
import functools
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
    last_id: SseEventId = dc.xfield(b'', repr_fn=dc.truthy_repr)


_DIGIT_BYTES = string.digits.encode('ascii')


class SseDecoder:
    """https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation"""

    def __init__(self) -> None:
        super().__init__()

        self._reset()
        self._last_event_id = b''
        self._reconnection_time: int | None = None

    _event_type: bytes
    _data: list[bytes]

    def _reset(self) -> None:
        self._event_type = b'message'
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
        if b'\r' in line or b'\n' in line:
            raise ValueError(line)

        if not line:
            yield self._dispatch_event()

        elif line[0] == b':'[0]:
            yield SseComment(line)

        elif (c := line.find(b':')) >= 0:
            d = c + 1
            if len(line) > d and line[d] == b' '[0]:
                d += 1
            self._process_field(line[:c], line[d:])

        else:
            self._process_field(line, b'')


_message_event = functools.partial(SseEvent, b'message')


TESTS = [
    (
        [
            b'data: YHOO',
            b'data: +2',
            b'data: 10',
            b'',
        ],
        [
            _message_event(b'YHOO\n+2\n10'),
        ],
    ),
    (
        [
            b': test stream',
            # b'',  # FIXME: ???
            b'data: first event',
            b'id: 1',
            b'',
            b'data:second event',
            b'id',
            b'',
            b'data:  third event',
            b'',
        ],
        [
            SseComment(b': test stream'),
            _message_event(b'first event', last_id=b'1'),
            _message_event(b'second event'),
            _message_event(b' third event'),
        ],
    ),
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
    [
        b'event: add',
        b'data: 73857293',
        b'',
        b'event: remove',
        b'data: 2153',
        b'',
        b'event: add',
        b'data: 113411',
        b'',
    ],
]


def _main() -> None:
    for test, expected in TESTS:
        dec = SseDecoder()
        output = [
            event
            for line in test
            for event in dec.process_line(line)
        ]
        print(output)
        print()
        assert output == expected


if __name__ == '__main__':
    _main()
