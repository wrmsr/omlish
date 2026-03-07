# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import enum
import ssl
import typing as ta

from ...streams.utils import ByteStreamBuffers
from ..bytes.buffering import InboundBytesBufferingIoPipelineHandler
from ..bytes.buffering import OutboundBytesBufferingIoPipelineHandler
from ..core import IoPipelineHandlerContext
from ..core import IoPipelineMessages
from ..flow.types import IoPipelineFlow
from ..flow.types import IoPipelineFlowMessages


##


class SslIoPipelineHandler(
    InboundBytesBufferingIoPipelineHandler,
    OutboundBytesBufferingIoPipelineHandler,
):
    """
    TLS via ssl.MemoryBIO + SSLObject.

    Model:
      - inbound bytes  : TLS records from transport -> feed into in_bio
      - outbound bytes : TLS records to transport   <- drained from out_bio
      - decrypted plaintext bytes are fed inbound (ctx.feed_in)
      - plaintext to encrypt bytes arrive outbound (outbound())

    TODO:
     - overhaul this thing gawd
     - shutdown timeout
     - context.set_alpn_protocols(['http/1.1'])
     - context.post_handshake_auth = True ?
    """

    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['SslIoPipelineHandler.Config']

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
            config = SslIoPipelineHandler.Config.DEFAULT
        self._config = config

    #

    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        return 0 if self._state is None else self._in_bio.pending

    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        return self._pending_outbound_bytes + (0 if self._state is None else self._out_bio.pending)

    #

    class State(enum.Enum):
        NEW = 'new'
        HANDSHAKE = 'handshake'
        ESTABLISHED = 'established'
        SHUTTING_DOWN = 'shutting_down'
        CLOSED = 'closed'

    _state: State

    @property
    def state(self) -> ta.Optional[State]:
        try:
            return self._state
        except AttributeError:
            return None

    _in_bio: ssl.MemoryBIO
    _out_bio: ssl.MemoryBIO

    _ssl_obj: ssl.SSLObject

    # Plaintext writes that we couldn't complete yet (usually because handshake isn't established, or write hit
    # WANT_READ and we're waiting for peer).
    _pending_plaintext_out: ta.List[ta.Any]
    _pending_outbound_bytes = 0

    _is_ready_for_input: bool = False
    _read_requested = False

    _inbound_eof_sent = False

    def _ensure_state(self) -> State:
        try:
            return self._state
        except AttributeError:
            pass

        self._in_bio = ssl.MemoryBIO()
        self._out_bio = ssl.MemoryBIO()
        self._ssl_obj = self._ssl_ctx.wrap_bio(
            self._in_bio,
            self._out_bio,
            server_side=self._server_side,
            server_hostname=self._server_hostname,
            session=self._ssl_session,
        )

        self._pending_plaintext_out = []

        self._state = self.State.NEW
        return self._state

    #

    def _fc(self, ctx: IoPipelineHandlerContext) -> ta.Optional[IoPipelineFlow]:
        return ctx.services.find(IoPipelineFlow)

    def _is_auto_read(self, ctx: IoPipelineHandlerContext) -> bool:
        if (flow := ctx.services.find(IoPipelineFlow)) is None:
            return True
        return flow.is_auto_read()

    #

    def _maybe_send_ready_for_input(self, ctx: IoPipelineHandlerContext) -> None:
        fc = self._fc(ctx)
        if fc is None or fc.is_auto_read():
            return

        # REASON 1: Handshake is stalled waiting for peer bytes. We must bridge this gap because the 'App' hasn't asked
        # for data yet.
        if self._state in (self.State.NEW, self.State.HANDSHAKE) and self._is_ready_for_input:
            self._is_ready_for_input = False
            ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())
            return

        # REASON 2: Downstream asked for data (_read_requested), but our internal BIO and SSL buffers are dry
        # (_is_ready_for_input).
        if self._state == self.State.ESTABLISHED and self._read_requested and self._is_ready_for_input:
            # Only request more from transport if the BIO isn't already EOF-ed
            if self._in_bio.pending == 0 and not self._in_bio.eof:
                self._is_ready_for_input = False
                # We don't reset _read_requested here! We keep it True so that when the bytes eventually arrive,
                # inbound() knows to pump them.
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

    def _pump_plaintext_in(self, ctx: IoPipelineHandlerContext) -> bool:
        """Read decrypted data from SSLObject -> inbound plaintext."""

        # We pump if we have a reason to:
        # 1. Auto-read is on.
        # 2. Downstream explicitly asked (_read_requested).
        # 3. We are handshaking (SSL engine is the consumer).

        produced = False

        while self._is_auto_read(ctx) or self._read_requested or self._state != self.State.ESTABLISHED:
            try:
                b = self._ssl_obj.read(self._config.read_chunk_size)

            except ssl.SSLWantReadError:
                # The SSL machine needs more ciphertext from the wire to progress.
                self._is_ready_for_input = True
                break

            except ssl.SSLWantWriteError:
                # Renegotiation or handshake needs to flush TLS records.
                self._pump_tls_out(ctx)
                break

            except ssl.SSLZeroReturnError:
                b = b''

            except ssl.SSLError as e:  # noqa
                # Robustness: fatal SSL errors should propagate to blow up the pipeline.
                raise

            if not b:
                # 1. Clear the manual read token
                if not self._is_auto_read(ctx):
                    self._read_requested = False

                # 2. Emit the synthetic FinalInput EXACTLY ONCE
                if not self._inbound_eof_sent:
                    self._inbound_eof_sent = True
                    ctx.feed_in(IoPipelineMessages.FinalInput())
                    # A FinalInput satisfies the read, but we DO NOT want to trigger a FlushInput in outbound().
                    return False

                break  # Already sent EOF, stop pumping

            # SUCCESS: We got plaintext.
            produced = True
            if self._state == self.State.ESTABLISHED:
                # Satisfy the 'ReadyForInput' token.
                if not self._is_auto_read(ctx):
                    self._read_requested = False

                ctx.feed_in(b)

                # In manual mode, we stop after one successful emission to satisfy Netty's 'one-read-per-request'
                # contract.
                if not self._is_auto_read(ctx):
                    return True

        return produced

    def _pump_tls_out(self, ctx: IoPipelineHandlerContext) -> None:
        """Drain out_bio -> outbound TLS records."""

        fo: ta.List[ta.Any] = []

        n = 0
        while True:
            b = self._out_bio.read()
            if not b:
                break
            fo.append(b)
            n += 1

        if self._out_bio.eof and self._state != self.State.CLOSED:
            # The SSL engine has finished its shutdown sequence (sent close_notify).
            self._state = self.State.CLOSED
            self._pending_plaintext_out.clear()
            self._pending_outbound_bytes = 0

        if (
                self._state in (self.State.HANDSHAKE, self.State.CLOSED) and
                n and
                self._fc(ctx) is not None
        ):
            fo.append(IoPipelineFlowMessages.FlushOutput())

        if self._state == self.State.CLOSED and self._pending_final_output is not None:
            fo.append(self._pending_final_output)
            self._pending_final_output = None

        for msg in fo:
            ctx.feed_out(msg)

    def _handshake_step(self, ctx: IoPipelineHandlerContext) -> bool:
        """Try to advance handshake. Returns True if established. Always pumps TLS output after attempting handshake."""

        if self._state == self.State.CLOSED:
            return False

        if self._state == self.State.NEW:
            self._state = self.State.HANDSHAKE

        if self._state == self.State.HANDSHAKE:
            try:
                self._ssl_obj.do_handshake()

            except ssl.SSLWantReadError:
                # Need peer bytes; but we also may have generated output.
                self._pump_tls_out(ctx)
                self._is_ready_for_input = True
                return False

            except ssl.SSLWantWriteError:
                # Need to flush our pending handshake records.
                self._pump_tls_out(ctx)
                return False

            self._state = self.State.ESTABLISHED
            # Handshake completion can still leave TLS output pending.
            self._pump_tls_out(ctx)
            return True

        return self._state == self.State.ESTABLISHED

    def _write_plaintext(self, ctx: IoPipelineHandlerContext, data: ta.Any) -> bool:
        """
        Write plaintext into SSLObject (encrypt). Returns True if fully accepted.
        On WANT_READ, caller should wait for inbound TLS.
        On WANT_WRITE, caller should flush out_bio.
        """

        for mv in ByteStreamBuffers.iter_segments(data):
            while True:
                try:
                    self._ssl_obj.write(mv)
                    break

                except ssl.SSLWantWriteError:
                    self._pump_tls_out(ctx)
                    # retry same mv
                    continue

                except ssl.SSLWantReadError:
                    self._is_ready_for_input = True
                    return False

        return True

    def _drain_pending_plaintext_out(self, ctx: IoPipelineHandlerContext) -> None:
        if not self._pending_plaintext_out:
            return
        if self._state != self.State.ESTABLISHED:
            return

        # Try to push everything; if we get WANT_READ mid-way, keep remainder.
        new_q: ta.List[ta.Any] = []
        new_b = 0
        for item in self._pending_plaintext_out:
            ok = self._write_plaintext(ctx, item)
            self._pump_tls_out(ctx)
            if not ok:
                new_q.append(item)
                new_b += len(item)
        self._pending_plaintext_out = new_q
        self._pending_outbound_bytes = new_b

    #

    _pending_final_output: ta.Any = None

    def _on_inbound_flush_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineFlowMessages.FlushInput) -> None:  # noqa
        self._ensure_state()

        self._maybe_send_ready_for_input(ctx)

        if self._state in (self.State.NEW, self.State.HANDSHAKE):
            return

        ctx.feed_in(msg)

    def _on_inbound_final_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineMessages.FinalInput) -> None:  # noqa
        self._ensure_state()

        # Signal EOF to the incoming BIO; this is the correct way to tell SSLObject there will be no more peer
        # bytes.
        try:
            self._in_bio.write_eof()
        except Exception as e:  # FIXME:  # noqa
            raise

        # Drain what we can: may emit decrypted tail, and/or TLS close_notify output.
        self._handshake_step(ctx)
        self._pump_plaintext_in(ctx)
        self._pump_tls_out(ctx)

        # If the engine is still technically self.State.ESTABLISHED but the transport is gone, we must force a
        # transition to prevent stuck buffers.
        if self._state != self.State.CLOSED:
            self._state = self.State.CLOSED
            self._pending_plaintext_out.clear()

        # If we reach EOF, any pending manual read request is effectively satisfied by 'nothing'. Clear it so we
        # don't try to ask the already-closed transport for more.
        self._read_requested = False

        # If an abrupt disconnect happened, ensure downstream gets an EOF
        if not self._inbound_eof_sent:
            self._inbound_eof_sent = True
            ctx.feed_in(IoPipelineMessages.FinalInput())

        # CONSUME the transport's FinalInput to prevent duplicate EOFs downstream
        ctx.mark_propagated('inbound', msg)

    def _on_inbound_bytes(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._ensure_state()

        # Feed ciphertext into in_bio.
        for mv in ByteStreamBuffers.iter_segments(msg):
            self._in_bio.write(mv)

        # Advance handshake if needed.
        established = self._handshake_step(ctx)

        if self._state == self.State.SHUTTING_DOWN:
            try:
                self._ssl_obj.unwrap()
                self._state = self.State.CLOSED
            except (ssl.SSLWantReadError, ssl.SSLWantWriteError):
                pass
            except Exception:  # FIXME:  # noqa
                self._state = self.State.CLOSED

        if established:
            # If we had buffered outbound plaintext while handshaking, try it now.
            self._drain_pending_plaintext_out(ctx)

        # Always pump: decrypted plaintext inbound, then any TLS output outbound.
        self._pump_plaintext_in(ctx)
        self._pump_tls_out(ctx)

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.FlushInput):
            self._on_inbound_flush_input(ctx, msg)
            return

        # Underlying transport EOF.
        if isinstance(msg, IoPipelineMessages.FinalInput):
            self._on_inbound_final_input(ctx, msg)
            return

        if ByteStreamBuffers.can_bytes(msg):
            self._on_inbound_bytes(ctx, msg)
            return

        ctx.feed_in(msg)

    #

    def _on_outbound_ready_for_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineFlowMessages.ReadyForInput) -> None:  # noqa
        self._ensure_state()

        # Mark that downstream wants data
        self._read_requested = True

        if self._state == self.State.ESTABLISHED:
            # Check if we actually satisfied the request
            if self._pump_plaintext_in(ctx):
                if not self._is_auto_read(ctx):
                    ctx.feed_in(IoPipelineFlowMessages.FlushInput())
                return  # Swallow

        if self._state == self.State.CLOSED:
            return

        # If we couldn't satisfy it (or we are handshaking), pass it up.
        ctx.feed_out(msg)

    def _on_outbound_flush_output(self, ctx: IoPipelineHandlerContext, msg: IoPipelineFlowMessages.FlushOutput) -> None:  # noqa
        ctx.feed_out(msg)

    def _on_outbound_final_output(self, ctx: IoPipelineHandlerContext, msg: IoPipelineMessages.FinalOutput) -> None:  # noqa
        self._ensure_state()

        if self._state in (self.State.ESTABLISHED, self.State.HANDSHAKE):
            try:
                # This initiates the TLS close_notify alert
                self._ssl_obj.unwrap()
                self._state = self.State.CLOSED

            except (ssl.SSLWantReadError, ssl.SSLWantWriteError) as se:
                self._state = self.State.SHUTTING_DOWN
                if isinstance(se, ssl.SSLWantReadError):
                    self._is_ready_for_input = False
                    ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())
                # Save the FinalOutput; we'll feed it once unwrap completes.
                self._pending_final_output = msg
                ctx.mark_propagated('outbound', msg)
                self._pump_tls_out(ctx)
                return

            except Exception:  # FIXME:  # noqa
                pass

            self._pump_tls_out(ctx)

        ctx.feed_out(msg)

    def _on_outbound_bytes(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._ensure_state()

        if self._state == self.State.CLOSED:
            # Handshake or close_notify already finalized. We can't encrypt more; drop or raise.
            self._pending_plaintext_out.clear()
            self._pending_outbound_bytes = 0
            return

        established = self._handshake_step(ctx)

        if not established:
            self._pending_plaintext_out.append(msg)
            self._pending_outbound_bytes += len(msg)
            self._maybe_send_ready_for_input(ctx)
            return

        # Write and check for WANT_READ (Renegotiation)
        ok = self._write_plaintext(ctx, msg)
        self._pump_tls_out(ctx)

        if not ok:
            self._pending_plaintext_out.append(msg)
            self._pending_outbound_bytes += len(msg)

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.ReadyForInput):
            self._on_outbound_ready_for_input(ctx, msg)
            return

        if isinstance(msg, IoPipelineFlowMessages.FlushOutput):
            self._on_outbound_flush_output(ctx, msg)
            return

        if isinstance(msg, IoPipelineMessages.FinalOutput):
            self._on_outbound_final_output(ctx, msg)
            return

        if ByteStreamBuffers.can_bytes(msg):
            self._on_outbound_bytes(ctx, msg)
            return

        ctx.feed_out(msg)
