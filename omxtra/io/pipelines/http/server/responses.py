# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import io
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.versions import HttpVersion

from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ..responses import FullPipelineHttpResponse


##


class PipelineHttpResponseEncoder(ChannelPipelineHandler):
    """
    Encodes FullPipelineHttpResponse into HTTP/1.x wire format bytes.

    Outbound:
      - FullPipelineHttpResponse -> bytes (status line + headers + body)
      - All other messages pass through unchanged

    Does not modify Content-Length or Connection headers - assumes the application has set them appropriately.
    """

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, FullPipelineHttpResponse):
            ctx.feed_out(msg)
            return

        head = msg.head
        body = msg.body

        buf = io.BytesIO()

        # Status line: HTTP/1.1 200 OK\r\n
        buf.write(self._encode_status_line(head.version, head.status, head.reason))

        # Headers: each as "Name: value\r\n"
        for hl in self._encode_headers(head.headers):
            buf.write(hl)

        # Blank line
        buf.write(b'\r\n')

        # Combine: status + headers + blank + body
        buf.write(body)

        ctx.feed_out(buf.getvalue())

    def _encode_status_line(self, version: HttpVersion, status: int, reason: str) -> bytes:
        """Encode HTTP status line: 'HTTP/1.1 200 OK\r\n'."""

        version_str = f'HTTP/{version.major}.{version.minor}'
        return f'{version_str} {status} {reason}\r\n'.encode('ascii')

    def _encode_headers(self, headers: HttpHeaders) -> ta.List[bytes]:
        """Encode headers as 'Name: value\r\n' lines."""

        lines: ta.List[bytes] = []

        # HttpHeaders stores entries as list of (name, value) tuples
        for name, value in headers.raw:
            # Header names and values should be ASCII-safe in practice
            line = f'{name}: {value}\r\n'.encode('ascii')
            lines.append(line)

        return lines
