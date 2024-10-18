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
        self._last_event_id = None

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

    def _dispatch_event(self) -> ta.Sequence[SseEvent]:
        raise NotImplementedError

    def process_line(self, line: bytes) -> ta.Iterable[SseDecoderOutput]:
        if not line:
            yield from self._dispatch_event()

        elif line[0] == b':':
            yield SseComment(line)

        elif (c := line.find(b':')) >= 0:
            if len(line) > c + 1 and line[c] == b' ':
                c += 1
            self._process_field(line[:c], line[c + 1:])

        else:
            self._process_field(line, b'')


LINES = [
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"role":"assistant","content":"","refusal":null},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":"Hello"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":"!"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":" How"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":" can"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":" I"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":" assist"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":" you"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":" today"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{"content":"?"},"logprobs":null,"finish_reason":null}]}',
    b'',
    b'data: {"id":"chatcmpl-AJnDGfUrocOB37bgHotqdYxZVJjLp","object":"chat.completion.chunk","created":1729280770,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_e2bde53e6e","choices":[{"index":0,"delta":{},"logprobs":null,"finish_reason":"stop"}]}',
    b'',
    b'data: [DONE]',
    b'',
    b'',
]


def _main() -> None:
    dec = SseDecoder()
    for line in LINES:
        print(list(dec(line)))


if __name__ == '__main__':
    _main()
