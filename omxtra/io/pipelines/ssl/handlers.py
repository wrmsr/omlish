# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import ssl
import typing as ta

from omlish.lite.check import check
from omlish.io.streams.utils import ByteStreamBuffers

from ..core import ChannelPipelineMessages
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

    def _drain_ssl_obj(self, ctx: ChannelPipelineHandlerContext, st: _State) -> None:
        fi: ta.List[ta.Any] = []
        fo: ta.List[ta.Any] = []

        wr = False
        ww = False
        nw = 0
        while True:
            try:
                b = st.obj.read(65536)  # FIXME: lol
            except ssl.SSLWantReadError:
                wr = True
                break
            except ssl.SSLWantWriteError:
                ww = True
                break
            if not b:
                raise NotImplementedError
            fi.append(b)
            nw += 1
        if nw and ctx.services.find(ChannelPipelineFlow) is not None:
            fi.append(ChannelPipelineFlowMessages.FlushInput())
        if wr:
            if (fc := ctx.services.find(ChannelPipelineFlow)) is not None and not fc.is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())
        if ww:
            pass  # nothing to be done?

        nr = 0
        while b := st.out_bio.read():
            fo.append(b)
            nr += 1
        del b
        if nr and ctx.services.find(ChannelPipelineFlow) is not None:
            fo.append(ChannelPipelineFlowMessages.FlushOutput())

        for msg in fi:
            ctx.feed_in(msg)
        for msg in fo:
            ctx.feed_out(msg)

    def _write_ssl_obj(self, ctx: ChannelPipelineHandlerContext, st: _State, data: ta.Any) -> None:
        for mv in ByteStreamBuffers.iter_segments(data):
            try:
                st.obj.write(mv)
            except ssl.SSLWantReadError:
                if (fc := ctx.services.find(ChannelPipelineFlow)) is not None and not fc.is_auto_read():
                    ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

    def _drain_post_handshake_write_buf(self, ctx: ChannelPipelineHandlerContext, st: _State) -> None:
        check.state(st.state == 'established')

        if not self._post_handshake_write_buf:
            return

        for hw in self._post_handshake_write_buf:
            self._write_ssl_obj(ctx, st, hw)
        del hw
        self._drain_ssl_obj(ctx, st)
        self._post_handshake_write_buf.clear()

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            if (st := self._state) is None:
                ctx.feed_in(msg)
                return

            st.obj.write(b'')
            self._drain_ssl_obj(ctx, st)
            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            # FIXME: honor lol
            ctx.feed_in(msg)
            return

        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        if (st := self._state) is None:
            st = self._state = self._new_state()

        if st.state == 'new':
            st.state = 'handshake'

        if st.state == 'handshake':
            self._write_ssl_obj(ctx, st, msg)
            try:
                st.obj.do_handshake()
            except ssl.SSLWantReadError:
                self._drain_ssl_obj(ctx, st)
                return
            except ssl.SSLWantWriteError:
                raise NotImplementedError from None
            st.state = 'established'
            self._drain_post_handshake_write_buf(ctx, st)
            return

        check.state(st.state == 'established')

        self._write_ssl_obj(ctx, st, msg)
        self._drain_ssl_obj(ctx, st)

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
                self._drain_ssl_obj(ctx, st)
                return
            except ssl.SSLWantWriteError:
                raise NotImplementedError from None
            st.state = 'established'
            self._drain_post_handshake_write_buf(ctx, st)

        check.state(st.state == 'established')

        raise NotImplementedError
