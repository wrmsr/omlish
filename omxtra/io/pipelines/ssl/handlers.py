# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import ssl
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages


##


class SslChannelPipelineHandler(ChannelPipelineHandler):
    def __init__(
            self,
            ssl_ctx: ta.Optional[ssl.SSLContext] = None,
            ssl_kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> None:
        super().__init__()

        if ssl_ctx is None:
            ssl_ctx = ssl.create_default_context()
        self._ssl_ctx = ssl_ctx
        self._ssl_kwargs = ssl_kwargs

        self._post_handshake_write_buf: ta.List[ta.Any] = []

    #

    @dc.dataclass()
    class _State:
        state: ta.Literal['new', 'handshake', 'established']
        obj: ssl.SSLObject
        in_bio: ssl.MemoryBIO
        out_bio: ssl.MemoryBIO

    def _new_state(self) -> _State:
        in_bio = ssl.MemoryBIO()
        out_bio = ssl.MemoryBIO()
        obj = self._ssl_ctx.wrap_bio(in_bio, out_bio, **(self._ssl_kwargs or {}))

        return self._State(
            'new',
            obj,
            in_bio,
            out_bio,
        )

    _state: ta.Optional[_State] = None

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        if (st := self._state) is None:
            st = self._state = self._new_state()

        if st.state == 'new':
            st.state = 'handshake'

        if st.state == 'handshake':
            try:
                st.obj.do_handshake()
            except ssl.SSLWantReadError:
                if (fc := ctx.services.find(ChannelPipelineFlow)) is not None and not fc.is_auto_read():
                    ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())
                return
            except ssl.SSLWantWriteError:
                raise NotImplementedError from None

        raise NotImplementedError

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        if (st := self._state) is None:
            st = self._state = self._new_state()

        if st.state == 'new':
            st.state = 'handshake'

        if st.state == 'handshake':
            self._post_handshake_write_buf.append(msg)
            try:
                st.obj.do_handshake()
            except ssl.SSLWantReadError:
                if (fc := ctx.services.find(ChannelPipelineFlow)) is not None and not fc.is_auto_read():
                    ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())
                return
            except ssl.SSLWantWriteError:
                raise NotImplementedError from None

        raise NotImplementedError
