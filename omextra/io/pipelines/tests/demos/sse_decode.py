# ruff: noqa: UP006
import typing as ta

from ...core import PipelineChannel
from ...decoders import DelimiterFrameDecoder
from ...decoders import StripLineEndings
from ...decoders import Utf8Decode
from ...http.responses import HttpResponseConditionalGzipDecompressor
from ...http.responses import HttpResponseDecoder
from ...http.sse import SseDecoder


##


def build_http_sse_channel() -> PipelineChannel:
    """Example: raw bytes -> HTTP response head -> conditional gzip -> longest-match line framing -> Sse events."""

    return PipelineChannel([
        HttpResponseDecoder(),
        HttpResponseConditionalGzipDecompressor(),
        DelimiterFrameDecoder([b'\r\n', b'\n'], keep_ends=True, max_size=1 << 20),
        Utf8Decode(),
        StripLineEndings(),
        SseDecoder(),
    ])


def demo_sync_http_sse() -> ta.List[ta.Any]:
    """
    Sync demo: feed bytes and return channel app outputs.

    In real usage, a transport driver would:
      - call channel.want_read() before reading
      - call channel.feed_bytes(...)
      - write channel.drain_outbound() to the socket
      - deliver channel.poll_app()/drain_app() to application logic
    """

    ch = build_http_sse_channel()

    raw = (
        b'HTTP/1.1 200 OK\r\n'
        b'Content-Type: text/event-stream\r\n'
        b'Cache-Control: no-cache\r\n'
        b'\r\n'
        b'event: message\n'
        b'data: hello\n'
        b'data: world\n\n'
        b'data: lone\n\n'
    )

    out: ta.List[ta.Any] = []
    for c in (raw[:25], raw[25:60], raw[60:90], raw[90:]):
        ch.feed_in(c)
        out.extend(ch.drain_out())

    ch.feed_eof()
    out.extend(ch.drain_out())
    return out


if __name__ == '__main__':
    print(demo_sync_http_sse())
