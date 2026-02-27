# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import ssl
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from ..bytes.buffering import OutboundBytesBufferingChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages


##


class SslChannelPipelineHandler(OutboundBytesBufferingChannelPipelineHandler):
    """
    TLS via ssl.MemoryBIO + SSLObject.

    Model:
      - inbound bytes  : TLS records from transport -> feed into in_bio
      - outbound bytes : TLS records to transport   <- drained from out_bio
      - decrypted plaintext bytes are fed inbound (ctx.feed_in)
      - plaintext to encrypt bytes arrive outbound (outbound())
    """

    def __init__(
            self,
            ssl_ctx: ta.Optional[ssl.SSLContext] = None,
            *,
            server_side: bool,
            server_hostname: ta.Optional[str] = None,
            ssl_session: ta.Optional[ssl.SSLSession] = None,
    ) -> None:
        super().__init__()

        if ssl_ctx is None:
            ssl_ctx = ssl.create_default_context()
        self._ssl_ctx = ssl_ctx
        self._server_side = server_side
        self._server_hostname = server_hostname
        self._ssl_session = ssl_session

        # Plaintext writes that we couldn't complete yet (usually because handshake isn't established, or write hit
        # WANT_READ and we're waiting for peer).
        self._pending_plaintext_out: ta.List[ta.Any] = []
        self._pending_outbound_bytes = 0
    #

    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        return self._pending_outbound_bytes

    #

    @dc.dataclass()
    class _State:
        state: ta.Literal['new', 'handshake', 'established', 'closed']
        obj: ssl.SSLObject
        in_bio: ssl.MemoryBIO
        out_bio: ssl.MemoryBIO

    _state: ta.Optional[_State] = None

    def _ensure_state(self) -> _State:
        if self._state is not None:
            return self._state
        in_bio = ssl.MemoryBIO()
        out_bio = ssl.MemoryBIO()
        obj = self._ssl_ctx.wrap_bio(
            in_bio,
            out_bio,
            server_side=self._server_side,
            server_hostname=self._server_hostname,
            session=self._ssl_session,
        )
        self._state = st = self._State('new', obj, in_bio, out_bio)
        return st

    #

    def _fc(self, ctx: ChannelPipelineHandlerContext) -> ta.Optional[ChannelPipelineFlow]:
        return ctx.services.find(ChannelPipelineFlow)

    def _maybe_ready_for_input(self, ctx: ChannelPipelineHandlerContext) -> None:
        fc = self._fc(ctx)
        if fc is not None and not fc.is_auto_read():
            ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

    #

    def _pump_tls_out(self, ctx: ChannelPipelineHandlerContext, st: _State) -> None:
        """Drain out_bio -> outbound TLS records."""

        fo: ta.List[ta.Any] = []

        n = 0
        while True:
            b = st.out_bio.read()
            if not b:
                break
            fo.append(b)
            n += 1

        if n and self._fc(ctx) is not None:
            fo.append(ChannelPipelineFlowMessages.FlushOutput())

        for msg in fo:
            ctx.feed_out(msg)

    def _pump_plaintext_in(self, ctx: ChannelPipelineHandlerContext, st: _State) -> None:
        """Read decrypted data from SSLObject -> inbound plaintext."""

        fi: ta.List[ta.Any] = []
        n = 0

        while True:
            try:
                b = st.obj.read(65536)
            except ssl.SSLWantReadError:
                # Need more TLS input from peer
                self._maybe_ready_for_input(ctx)
                break
            except ssl.SSLWantWriteError:
                # Need to write pending TLS output (renegotiation / handshake)
                self._pump_tls_out(ctx, st)
                # try again next time we get called
                break

            if not b:
                # TLS-level EOF (close_notify) or underlying EOF was processed.
                # We don't force-close pipeline here; just stop pumping.
                break

            fi.append(b)
            n += 1

        if n and self._fc(ctx) is not None:
            fi.append(ChannelPipelineFlowMessages.FlushInput())

        for msg in fi:
            ctx.feed_in(msg)

    def _handshake_step(self, ctx: ChannelPipelineHandlerContext, st: _State) -> bool:
        """
        Try to advance handshake. Returns True if established. Always pumps TLS output after attempting handshake.
        """

        if st.state == 'closed':
            return False

        if st.state == 'new':
            st.state = 'handshake'

        if st.state == 'handshake':
            try:
                st.obj.do_handshake()
            except ssl.SSLWantReadError:
                # Need peer bytes; but we also may have generated output.
                self._pump_tls_out(ctx, st)
                self._maybe_ready_for_input(ctx)
                return False
            except ssl.SSLWantWriteError:
                # Need to flush our pending handshake records.
                self._pump_tls_out(ctx, st)
                return False

            st.state = 'established'
            # Handshake completion can still leave TLS output pending.
            self._pump_tls_out(ctx, st)
            return True

        return st.state == 'established'

    def _write_plaintext(self, ctx: ChannelPipelineHandlerContext, st: _State, data: ta.Any) -> bool:
        """
        Write plaintext into SSLObject (encrypt). Returns True if fully accepted.
        On WANT_READ, caller should wait for inbound TLS.
        On WANT_WRITE, caller should flush out_bio.
        """

        for mv in ByteStreamBuffers.iter_segments(data):
            while True:
                try:
                    st.obj.write(mv)
                    break
                except ssl.SSLWantWriteError:
                    self._pump_tls_out(ctx, st)
                    # retry same mv
                    continue
                except ssl.SSLWantReadError:
                    self._maybe_ready_for_input(ctx)
                    return False
        return True

    def _drain_pending_plaintext_out(self, ctx: ChannelPipelineHandlerContext, st: _State) -> None:
        if not self._pending_plaintext_out:
            return
        if st.state != 'established':
            return

        # Try to push everything; if we get WANT_READ mid-way, keep remainder.
        new_q: ta.List[ta.Any] = []
        new_b = 0
        for item in self._pending_plaintext_out:
            ok = self._write_plaintext(ctx, st, item)
            self._pump_tls_out(ctx, st)
            if not ok:
                new_q.append(item)
                new_b += len(item)
        self._pending_plaintext_out = new_q
        self._pending_outbound_bytes = new_b

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        # Propagate flow control messages as-is.
        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            ctx.feed_in(msg)
            return

        # Underlying transport EOF.
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            st = self._state
            if st is None:
                ctx.feed_in(msg)
                return

            # Signal EOF to the incoming BIO; this is the correct way to tell SSLObject there will be no more peer
            # bytes.
            try:
                st.in_bio.write_eof()
            except Exception as e:  # FIXME:  # noqa
                raise

            # Drain what we can: may emit decrypted tail, and/or TLS close_notify output.
            self._handshake_step(ctx, st)
            self._pump_plaintext_in(ctx, st)
            self._pump_tls_out(ctx, st)

            ctx.feed_in(msg)
            return

        # If it's not bytes, just pass through.
        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        st = self._ensure_state()

        # Feed ciphertext into in_bio.
        for mv in ByteStreamBuffers.iter_segments(msg):
            st.in_bio.write(mv)

        # Advance handshake if needed.
        established = self._handshake_step(ctx, st)
        if established:
            # If we had buffered outbound plaintext while handshaking, try it now.
            self._drain_pending_plaintext_out(ctx, st)

        # Always pump: decrypted plaintext inbound, then any TLS output outbound.
        self._pump_plaintext_in(ctx, st)
        self._pump_tls_out(ctx, st)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        # Propagate flow control messages as-is.
        if isinstance(msg, ChannelPipelineFlowMessages.FlushOutput):
            ctx.feed_out(msg)
            return

        # If it's not bytes, pass through OUTBOUND (not inbound).
        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_out(msg)
            return

        st = self._ensure_state()

        # Ensure handshake has been started; for a client this is typically what causes "client shoots first" (we
        # generate ClientHello in out_bio).
        established = self._handshake_step(ctx, st)

        if not established:
            # Can't reliably write app-data yet; buffer and ensure handshake output is flushed.
            self._pending_plaintext_out.append(msg)
            self._pending_outbound_bytes += len(msg)
            self._pump_tls_out(ctx, st)
            return

        # Established: write plaintext -> TLS records, flush them.
        ok = self._write_plaintext(ctx, st, msg)
        self._pump_tls_out(ctx, st)

        if not ok:
            # We hit WANT_READ while writing; buffer and wait for peer bytes.
            self._pending_plaintext_out.append(msg)
            self._pending_outbound_bytes += len(msg)
            return
