# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import io
import typing as ta

from ...io.pipelines.core import IoPipelineHandler
from ...io.pipelines.core import IoPipelineHandlerContext
from ...lite.abstract import Abstract
from ..headers import HttpHeaders
from .objects import FullPipelineHttpMessage
from .objects import PipelineHttpMessageContentChunkData
from .objects import PipelineHttpMessageEnd
from .objects import PipelineHttpMessageHead
from .objects import PipelineHttpMessageObjects


##


class PipelineHttpObjectEncoder(
    PipelineHttpMessageObjects,
    IoPipelineHandler,
    Abstract,
):
    def __init__(self) -> None:
        super().__init__()

        self._streaming = False
        self._chunked = False

    #

    @abc.abstractmethod
    def _encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        raise NotImplementedError

    #

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, self._head_type):
            self._handle_request_head(ctx, msg)

        elif isinstance(msg, self._full_type):
            self._handle_full_request(ctx, msg)

        elif isinstance(msg, self._content_chunk_data_type):
            self._handle_content_chunk_data(ctx, msg)

        elif isinstance(msg, self._end_type):
            self._handle_request_end(ctx, msg)

        else:
            ctx.feed_out(msg)

    #

    def _handle_request_head(self, ctx: IoPipelineHandlerContext, msg: PipelineHttpMessageHead) -> None:  # noqa
        """Emit request line + headers, enter streaming mode."""

        self._streaming = True
        self._chunked = self._is_chunked(msg.headers)

        ctx.feed_out(self._encode_head(msg))

    #

    def _handle_full_request(self, ctx: IoPipelineHandlerContext, msg: FullPipelineHttpMessage) -> ta.Any:
        """Emit complete request in one shot."""

        ctx.feed_out(self._encode_head(msg.head))
        if len(msg.body) > 0:
            ctx.feed_out(msg.body)

    #

    def _handle_content_chunk_data(self, ctx: IoPipelineHandlerContext, msg: PipelineHttpMessageContentChunkData) -> None:  # noqa
        """Emit body chunk (raw or chunked-encoded)."""

        if not self._streaming:
            # Not in streaming mode - pass through unchanged
            ctx.feed_out(msg)

        elif len(msg.data) < 1:
            pass

        elif self._chunked:
            # Chunked encoding: <size-hex>\r\n<data>\r\n
            ctx.feed_out(f'{len(msg.data):x}\r\n'.encode('ascii'))
            ctx.feed_out(msg.data)
            ctx.feed_out(b'\r\n')

        else:
            # Raw data
            ctx.feed_out(msg.data)

    #

    def _handle_request_end(self, ctx: IoPipelineHandlerContext, msg: PipelineHttpMessageEnd) -> None:  # noqa
        """Emit terminator if chunked, reset state."""

        if not self._streaming:
            # Not in streaming mode - pass through
            ctx.feed_out(msg)
            return

        was_chunked = self._chunked

        # Reset state
        self._streaming = False
        self._chunked = False

        if was_chunked:
            # Emit final chunk: 0\r\n\r\n
            ctx.feed_out(b'0\r\n\r\n')

    #

    def _encode_head(self, head: PipelineHttpMessageHead) -> bytes:
        buf = io.BytesIO()

        buf.write(self._encode_head_line(head))

        for hl in self._encode_headers(head.headers):
            buf.write(hl)

        buf.write(b'\r\n')

        return buf.getvalue()

    def _encode_headers(self, headers: HttpHeaders) -> ta.List[bytes]:
        """Encode headers as 'Name: value\r\n' lines."""

        lines: ta.List[bytes] = []

        # HttpHeaders stores entries as list of (name, value) tuples
        for name, value in headers.raw:
            # Header names and values should be ASCII-safe in practice
            line = f'{name}: {value}\r\n'.encode('ascii')
            lines.append(line)

        return lines

    def _is_chunked(self, headers: HttpHeaders) -> bool:
        """Check if Transfer-Encoding includes 'chunked'."""

        te = headers.lower.get('transfer-encoding', ())
        return 'chunked' in te
