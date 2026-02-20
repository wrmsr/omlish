# ruff: noqa: UP006
# @omlish-lite
import abc
import typing as ta

from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineHandlerFn
from ..core import ShareableChannelPipelineHandler
from .errors import DecoderError
from .types import ChannelPipelineFlow
from .types import ChannelPipelineFlowMessages


##


class MessageToMessageDecoder(ChannelPipelineHandler, Abstract):
    @abc.abstractmethod
    def _should_decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def _decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
        raise NotImplementedError

    _decode_called = False
    _message_produced = False

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not isinstance(self, ShareableChannelPipelineHandler):
                if (
                        self._decode_called and
                        not self._message_produced and
                        not ctx.channel.services[ChannelPipelineFlow].is_auto_read
                ):
                    ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

                self._decode_called = False
                self._message_produced = False

            ctx.feed_in(msg)
            return

        self._decode_called = True

        out: ta.List[ta.Any] = []
        try:
            if self._should_decode(ctx, msg):
                out.extend(self._decode(ctx, msg))
            else:
                out.append(msg)

        except DecoderError:
            raise
        except Exception as e:
            raise DecoderError from e

        finally:
            self._message_produced |= bool(out)
            for out_msg in out:
                ctx.feed_in(out_msg)


##


class FnMessageToMessageDecoder(MessageToMessageDecoder):
    def __init__(
            self,
            filter_fn: ChannelPipelineHandlerFn[ta.Any, bool],  # noqa
            decode_fn: ChannelPipelineHandlerFn[ta.Any, ta.Iterable[ta.Any]],
    ) -> None:
        super().__init__()

        self._filter_fn = filter_fn
        self._decode_fn = decode_fn

    def _should_decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
        return self._filter_fn(ctx, msg)

    def _decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
        return self._decode_fn(ctx, msg)
