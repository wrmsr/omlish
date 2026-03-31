# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from ...io.pipelines.core import IoPipelineHandler
from ...io.pipelines.core import IoPipelineHandlerContext
from ...io.pipelines.core import IoPipelineMessages
from ...io.pipelines.flow.types import IoPipelineFlowMessages
from ...io.types import BytesLike
from ...lite.abstract import Abstract
from .objects import IoPipelineHttpMessageObjects


##


class IoPipelineHttpObjectChunker(
    IoPipelineHttpMessageObjects,
    IoPipelineHandler,
    Abstract,
):
    """
    Outbound handler that wraps BodyData messages in chunked transfer encoding framing (Chunk, EndChunk, LastChunk,
    ChunkedTrailers).

    Buffers outbound BodyData and flushes on FlushOutput, End, or when the buffer reaches an optional max_chunk_size.
    Sits between the Compressor and Encoder so that chunk sizes reflect compressed data sizes.
    """

    def __init__(self, *, max_chunk_size: ta.Optional[int] = None) -> None:
        super().__init__()

        self._max_chunk_size = max_chunk_size

        self._active = False
        self._buf: ta.List[BytesLike] = []
        self._buf_size = 0

    #

    def _reset(self) -> None:
        self._active = False
        self._buf.clear()
        self._buf_size = 0

    def _flush_buf(self, ctx: IoPipelineHandlerContext) -> None:
        if self._buf_size < 1:
            return

        ctx.feed_out(self._make_chunk(self._buf_size))
        for data in self._buf:
            ctx.feed_out(self._make_body_data(data))
        ctx.feed_out(self._make_end_chunk())

        self._buf = []
        self._buf_size = 0

    def _buffer_data(self, ctx: IoPipelineHandlerContext, data: BytesLike) -> None:
        dl = len(data)

        if (mcs := self._max_chunk_size) is not None and (self._buf_size + dl) > mcs:
            self._flush_buf(ctx)

        self._buf.append(data)
        self._buf_size += dl

        if mcs is not None and dl >= mcs:
            self._flush_buf(ctx)

    #

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, self._head_type):
            self._active = msg.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True)
            ctx.feed_out(msg)
            return

        if isinstance(msg, self._full_type):
            if msg.head.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True):
                ctx.feed_out(msg.head)

                if len(msg.body) > 0:
                    self._buffer_data(ctx, msg.body)

                self._flush_buf(ctx)
                ctx.feed_out(self._make_last_chunk())
                ctx.feed_out(self._make_chunked_trailers())
                ctx.feed_out(self._make_end())
                return

            ctx.feed_out(msg)
            return

        if self._active:
            if isinstance(msg, self._body_data_type):
                self._buffer_data(ctx, msg.data)
                return

            if isinstance(msg, IoPipelineFlowMessages.FlushOutput):
                self._flush_buf(ctx)
                ctx.feed_out(msg)
                return

            if isinstance(msg, self._end_type):
                self._flush_buf(ctx)
                ctx.feed_out(self._make_last_chunk())
                ctx.feed_out(self._make_chunked_trailers())
                self._reset()
                ctx.feed_out(msg)
                return

            if isinstance(msg, self._aborted_type):
                self._reset()
                ctx.feed_out(msg)
                return

            if isinstance(msg, IoPipelineMessages.FinalOutput):
                self._reset()
                ctx.feed_out(self._make_aborted('eof before end of message'))
                ctx.feed_out(msg)
                return

        ctx.feed_out(msg)


##


class IoPipelineHttpObjectDechunker(
    IoPipelineHttpMessageObjects,
    IoPipelineHandler,
    Abstract,
):
    """
    Inbound handler that strips chunked transfer encoding framing messages (Chunk, EndChunk, LastChunk,
    ChunkedTrailers), leaving only Head + BodyData* + End for downstream handlers.

    Sits between the Decoder and Decompressor in the pipeline so that the decompressor sees only content-level messages
    without stale chunk sizes.
    """

    def __init__(self) -> None:
        super().__init__()

        self._active = False

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, self._head_type):
            self._active = msg.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True)
            ctx.feed_in(msg)
            return

        if self._active and isinstance(msg, (
                self._chunk_type,
                self._end_chunk_type,
                self._last_chunk_type,
                self._chunked_trailers_type,
        )):
            return

        if isinstance(msg, (self._end_type, self._aborted_type)):
            self._active = False

        ctx.feed_in(msg)
