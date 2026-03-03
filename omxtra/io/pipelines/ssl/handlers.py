# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import ssl
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from ..bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ..bytes.buffering import OutboundBytesBufferingChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages


##


class SslChannelPipelineHandler(
    InboundBytesBufferingChannelPipelineHandler,
    OutboundBytesBufferingChannelPipelineHandler,
):
    """
    TLS via ssl.MemoryBIO + SSLObject.

    Model:
      - inbound bytes  : TLS records from transport -> feed into in_bio
      - outbound bytes : TLS records to transport   <- drained from out_bio
      - decrypted plaintext bytes are fed inbound (ctx.feed_in)
      - plaintext to encrypt bytes arrive outbound (outbound())

    TODO:
     - shutdown timeout
     - context.set_alpn_protocols(['http/1.1'])
     - context.post_handshake_auth = True ?
    """

    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['SslChannelPipelineHandler.Config']

        read_chunk_size: int = 64 * 1024

    Config.DEFAULT = Config()

    def __init__(
            self,
            ssl_ctx: ta.Optional[ssl.SSLContext] = None,
            *,
            server_side: bool,
            server_hostname: ta.Optional[str] = None,
            ssl_session: ta.Optional[ssl.SSLSession] = None,
            config: ta.Optional[Config] = None,
    ) -> None:
        super().__init__()

        if ssl_ctx is None:
            ssl_ctx = ssl.create_default_context()
        self._ssl_ctx = ssl_ctx
        self._server_side = server_side
        self._server_hostname = server_hostname
        self._ssl_session = ssl_session
        if config is None:
            config = SslChannelPipelineHandler.Config.DEFAULT
        self._config = config

        # Plaintext writes that we couldn't complete yet (usually because handshake isn't established, or write hit
        # WANT_READ and we're waiting for peer).
        self._pending_plaintext_out: ta.List[ta.Any] = []
        self._pending_outbound_bytes = 0

        self._inbound_eof_sent = False

    #

    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        return 0 if (st := self._state) is None else st.in_bio.pending

    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        return self._pending_outbound_bytes + (0 if (st := self._state) is None else st.out_bio.pending)

    #

    @dc.dataclass()
    class _State:
        state: ta.Literal['new', 'handshake', 'established', 'shutting_down', 'closed']
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

    def _is_auto_read(self, ctx: ChannelPipelineHandlerContext) -> bool:
        if (flow := ctx.services.find(ChannelPipelineFlow)) is None:
            return True
        return flow.is_auto_read()

    #

    _is_ready_for_input: bool = False
    _read_requested = False

    def _maybe_send_ready_for_input(self, ctx: ChannelPipelineHandlerContext) -> None:
        st = self._state
        if st is None:
            return

        fc = self._fc(ctx)
        if fc is None or fc.is_auto_read():
            return

        # REASON 1: Handshake is stalled waiting for peer bytes. We must bridge this gap because the 'App' hasn't asked
        # for data yet.
        if st.state in ('new', 'handshake') and self._is_ready_for_input:
            self._is_ready_for_input = False
            ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())
            return

        # REASON 2: Downstream asked for data (_read_requested), but our internal BIO and SSL buffers are dry
        # (_is_ready_for_input).
        if st.state == 'established' and self._read_requested and self._is_ready_for_input:
            # Only request more from transport if the BIO isn't already EOF-ed
            if st.in_bio.pending == 0 and not st.in_bio.eof:
                self._is_ready_for_input = False
                # We don't reset _read_requested here! We keep it True so that when the bytes eventually arrive,
                # inbound() knows to pump them.
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

    #

    def _pump_plaintext_in(self, ctx: ChannelPipelineHandlerContext, st: _State) -> bool:
        """Read decrypted data from SSLObject -> inbound plaintext."""

        # We pump if we have a reason to:
        # 1. Auto-read is on.
        # 2. Downstream explicitly asked (_read_requested).
        # 3. We are handshaking (SSL engine is the consumer).

        produced = False

        while self._is_auto_read(ctx) or self._read_requested or st.state != 'established':
            try:
                b = st.obj.read(self._config.read_chunk_size)
            except ssl.SSLWantReadError:
                # The SSL machine needs more ciphertext from the wire to progress.
                self._is_ready_for_input = True
                break
            except ssl.SSLWantWriteError:
                # Renegotiation or handshake needs to flush TLS records.
                self._pump_tls_out(ctx, st)
                break
            except ssl.SSLError:
                # Robustness: fatal SSL errors should propagate to blow up the channel.
                raise

            if not b:
                # 1. Clear the manual read token
                if not self._is_auto_read(ctx):
                    self._read_requested = False

                # 2. Emit the synthetic FinalInput EXACTLY ONCE
                if not self._inbound_eof_sent:
                    self._inbound_eof_sent = True
                    ctx.feed_in(ChannelPipelineMessages.FinalInput())
                    # A FinalInput satisfies the read, but we DO NOT want to trigger a FlushInput in outbound().
                    return False

                break  # Already sent EOF, stop pumping

            # SUCCESS: We got plaintext.
            produced = True
            if st.state == 'established':
                # Satisfy the 'ReadyForInput' token.
                if not self._is_auto_read(ctx):
                    self._read_requested = False

                ctx.feed_in(b)

                # In manual mode, we stop after one successful emission to satisfy Netty's 'one-read-per-request'
                # contract.
                if not self._is_auto_read(ctx):
                    return True

        return produced

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

        if st.out_bio.eof and st.state != 'closed':
            # The SSL engine has finished its shutdown sequence (sent close_notify).
            st.state = 'closed'
            self._pending_plaintext_out.clear()
            self._pending_outbound_bytes = 0

        if (
                st.state in ('handshake', 'closed') and
                n and
                self._fc(ctx) is not None
        ):
            fo.append(ChannelPipelineFlowMessages.FlushOutput())

        for msg in fo:
            ctx.feed_out(msg)

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
                self._is_ready_for_input = True
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
                    self._is_ready_for_input = True
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

    _pending_final_output: ta.Any = None

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            self._maybe_send_ready_for_input(ctx)

            if (st := self._state) is not None and st.state in ('new', 'handshake'):
                return

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

            # If the engine is still technically 'established' but the transport is gone, we must force a transition to
            # prevent stuck buffers.
            if st.state != 'closed':
                st.state = 'closed'
                self._pending_plaintext_out.clear()

            # If we reach EOF, any pending manual read request is effectively satisfied by 'nothing'. Clear it so we
            # don't try to ask the already-closed transport for more.
            self._read_requested = False

            # If an abrupt disconnect happened, ensure downstream gets an EOF
            if not self._inbound_eof_sent:
                self._inbound_eof_sent = True
                ctx.feed_in(ChannelPipelineMessages.FinalInput())

            # CONSUME the transport's FinalInput to prevent duplicate EOFs downstream
            ctx.mark_propagated('inbound', msg)
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

        if st.state == 'shutting_down':
            try:
                st.obj.unwrap()
                st.state = 'closed'
                if self._pending_final_output is not None:
                    ctx.feed_out(self._pending_final_output)
                    self._pending_final_output = None
            except (ssl.SSLWantReadError, ssl.SSLWantWriteError):
                pass
            except Exception:  # FIXME:  # noqa
                st.state = 'closed'

        if established:
            # If we had buffered outbound plaintext while handshaking, try it now.
            self._drain_pending_plaintext_out(ctx, st)

        # Always pump: decrypted plaintext inbound, then any TLS output outbound.
        self._pump_plaintext_in(ctx, st)
        self._pump_tls_out(ctx, st)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        # 1. Intercept ReadyForInput
        if isinstance(msg, ChannelPipelineFlowMessages.ReadyForInput):
            st = self._state
            if st is None:
                ctx.feed_out(msg)
                return

            if st.state == 'established':
                # Mark that downstream wants data
                self._read_requested = True

                # Check if we actually satisfied the request
                if self._pump_plaintext_in(ctx, st):
                    if not self._is_auto_read(ctx):
                        ctx.feed_in(ChannelPipelineFlowMessages.FlushInput())
                    return  # Swallow

            if st.state == 'closed':
                return

            # If we couldn't satisfy it (or we are handshaking), pass it up.
            ctx.feed_out(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushOutput):
            ctx.feed_out(msg)
            return

        if isinstance(msg, ChannelPipelineMessages.FinalOutput):
            st = self._state
            if st and st.state in ('established', 'handshake'):
                try:
                    # This initiates the TLS close_notify alert
                    st.obj.unwrap()
                    st.state = 'closed'
                except (ssl.SSLWantReadError, ssl.SSLWantWriteError):
                    st.state = 'shutting_down'
                    # Save the FinalOutput; we'll feed it once unwrap completes.
                    self._pending_final_output = msg
                    self._pump_tls_out(ctx, st)
                    return
                except Exception:  # FIXME:  # noqa
                    pass
                self._pump_tls_out(ctx, st)

            ctx.feed_out(msg)
            return

        # 2. Handle Plaintext Writes
        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_out(msg)
            return

        st = self._ensure_state()

        if st.state == 'closed':
            # Handshake or close_notify already finalized. We can't encrypt more; drop or raise.
            self._pending_plaintext_out.clear()
            self._pending_outbound_bytes = 0
            return

        established = self._handshake_step(ctx, st)

        if not established:
            self._pending_plaintext_out.append(msg)
            self._pending_outbound_bytes += len(msg)
            self._maybe_send_ready_for_input(ctx)
            return

        # Write and check for WANT_READ (Renegotiation)
        ok = self._write_plaintext(ctx, st, msg)
        self._pump_tls_out(ctx, st)

        if not ok:
            self._pending_plaintext_out.append(msg)
            self._pending_outbound_bytes += len(msg)
