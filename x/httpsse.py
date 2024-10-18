"""
TODO:
 - end-of-line   = ( cr lf / cr / lf )
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


@dc.dataclass(frozen=True)
class SseEvent(lang.Abstract):
    pass


class SseDecoder:
    """https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation"""

    def __init__(self) -> None:
        super().__init__()
        self._data: list[bytes] = []
        self._last_event_id: str | None = None

    def __call__(self, e: bytes) -> ta.Iterable[SseEvent]:
        raise NotImplementedError


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
