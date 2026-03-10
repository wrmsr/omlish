# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import io
import typing as ta

from ...io.pipelines.core import IoPipelineHandler
from ...io.pipelines.core import IoPipelineHandlerContext
from ...lite.abstract import Abstract
from ..headers import HttpHeaders
from .objects import FullIoPipelineHttpMessage
from .objects import IoPipelineHttpMessageBodyData
from .objects import IoPipelineHttpMessageChunk
from .objects import IoPipelineHttpMessageChunkedTrailers
from .objects import IoPipelineHttpMessageEnd
from .objects import IoPipelineHttpMessageEndChunk
from .objects import IoPipelineHttpMessageHead
from .objects import IoPipelineHttpMessageLastChunk
from .objects import IoPipelineHttpMessageObjects


##


class IoPipelineHttpObjectEncoder(
    IoPipelineHttpMessageObjects,
    IoPipelineHandler,
    Abstract,
):
    def __init__(self) -> None:
        super().__init__()

        self._streaming = False

    #

    @abc.abstractmethod
    def _encode_head_line(self, head: IoPipelineHttpMessageHead) -> bytes:
        raise NotImplementedError

    #

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, self._head_type):
            self._handle_request_head(ctx, msg)

        elif isinstance(msg, self._full_type):
            self._handle_full_request(ctx, msg)

        elif isinstance(msg, self._chunk_type):
            self._handle_chunk(ctx, msg)

        elif isinstance(msg, self._end_chunk_type):
            self._handle_end_chunk(ctx, msg)

        elif isinstance(msg, self._last_chunk_type):
            self._handle_last_chunk(ctx, msg)

        elif isinstance(msg, self._chunked_trailers_type):
            self._handle_chunked_trailers(ctx, msg)

        elif isinstance(msg, self._body_data_type):
            self._handle_body_data(ctx, msg)

        elif isinstance(msg, self._end_type):
            self._handle_request_end(ctx, msg)

        else:
            ctx.feed_out(msg)

    #

    def _handle_request_head(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageHead) -> None:  # noqa
        self._streaming = True

        ctx.feed_out(self._encode_head(msg))

    #

    def _handle_full_request(self, ctx: IoPipelineHandlerContext, msg: FullIoPipelineHttpMessage) -> ta.Any:
        ctx.feed_out(self._encode_head(msg.head))
        if len(msg.body) > 0:
            ctx.feed_out(msg.body)

    #

    def _handle_chunk(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageChunk) -> None:  # noqa
        ctx.feed_out(f'{msg.size:x}\r\n'.encode('ascii'))

    #

    def _handle_end_chunk(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageEndChunk) -> None:  # noqa
        ctx.feed_out(b'\r\n')

    #

    def _handle_last_chunk(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageLastChunk) -> None:  # noqa
        ctx.feed_out(b'0\r\n')

    #

    def _handle_chunked_trailers(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageChunkedTrailers) -> None:  # noqa
        ctx.feed_out(b'\r\n')

    #

    def _handle_body_data(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageBodyData) -> None:  # noqa
        if not self._streaming:
            # Not in streaming mode - pass through unchanged
            ctx.feed_out(msg)

        if len(msg.data) < 1:
            pass

        ctx.feed_out(msg.data)

    #

    def _handle_request_end(self, ctx: IoPipelineHandlerContext, msg: IoPipelineHttpMessageEnd) -> None:  # noqa
        if not self._streaming:
            # Not in streaming mode - pass through
            ctx.feed_out(msg)
            return

        # Reset state
        self._streaming = False

    #

    def _encode_head(self, head: IoPipelineHttpMessageHead) -> bytes:
        buf = io.BytesIO()

        buf.write(self._encode_head_line(head))

        for hl in self._encode_headers(head.headers):
            buf.write(hl)

        buf.write(b'\r\n')

        return buf.getvalue()

    def _encode_headers(self, headers: HttpHeaders) -> ta.List[bytes]:
        lines: ta.List[bytes] = []

        # HttpHeaders stores entries as list of (name, value) tuples
        for name, value in headers.raw:
            # Header names and values should be ASCII-safe in practice
            line = f'{name}: {value}\r\n'.encode('ascii')
            lines.append(line)

        return lines
