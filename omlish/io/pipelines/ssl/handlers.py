# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import collections
import dataclasses as dc
import enum
import ssl
import typing as ta

from ...streambufs.utils import ByteStreamBuffers
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
     - inbound bytes   : TLS records from transport -> written into in_bio
     - outbound bytes  : plaintext from app -> queued -> encrypted -> drained from out_bio toward transport
     - decrypted plaintext bytes are fed inbound (ctx.feed_in)

    Architecture - the whole point of this shape is that there are exactly three phases, always in the same order, no
    matter which event arrived:

     1. APPLY   - `inbound()` / `outbound()` entry points ONLY classify the message and mutate handler
                  state (write ciphertext into in_bio, enqueue plaintext, set a latch). They never advance the SSL
                  machine and never feed flow messages.

     2. PUMP    - `_pump()` advances the SSL machine to quiescence (handshake, writes, reads, shutdown -
                  looped while any step makes progress). Steps never touch `ctx`; they only mutate state and append
                  produced plaintext/ciphertext to lists. Every `WANT_READ` anywhere simply sets `_want_ciphertext`
                  (which is cleared and re-derived on every pump).

     3. EMIT    - `_emit()` is the ONLY place `ctx.feed_in` / `ctx.feed_out` is called for
                  machine-produced messages. It feeds the collected bytes and then derives all flow-control messages
                  (ReadyForInput, FlushInput, FlushOutput, ReadyForOutput / PauseOutput, deferred FinalInput /
                  FinalOutput) by diffing level-state against what was last announced. Flow logic lives here and nowhere
                  else.

    `_turn()` wraps pump+emit in a reentrancy guard: if delivering a message synchronously causes another event to
    arrive at this handler (app writes in response to plaintext, transport feeds more bytes in a loopback test, ...),
    the nested entry point just mutates state and flags the turn dirty; the outer turn loops until quiescent. Combined
    with emitting outbound ciphertext *before* inbound plaintext, this makes TLS record ordering on the wire immune to
    reentrancy.

    Flow-control behaviors (all only active when an `IoPipelineFlow` service is present):
     - Manual read (`ReadyForInput`, ~Netty `read()`): one plaintext delivery per token. The handler also autonomously
       requests transport reads whenever the engine itself is starved (handshake, shutdown awaiting the peer's
       close_notify, or an SSL_write blocked on WANT_READ during renegotiation/KeyUpdate), deduplicated via an
       outstanding-token latch.
     - Writability (`ReadyForOutput` / `PauseOutput`, ~Netty `channelWritabilityChanged`): level-triggered,
       edge-notified. The transport-side signal is combined with this handler's own plaintext backlog (hysteresis via
       `write_high_watermark` / `write_low_watermark`) and the *combined* signal is re-announced inbound on change.
       While unwritable, app plaintext is held in the queue un-encrypted (backpressure is kept where byte accounting is
       honest - encrypted bytes can't be un-sent); handshake / alert / close_notify records are exempt, as gating them
       would deadlock renegotiation and shutdown.

    Half-close is supported in both directions: after transport read-EOF the engine keeps serving any already-decrypted
    plaintext to later reads, and outbound writes remain legal until FinalOutput; after the peer's close_notify (clean
    read-EOF) writes likewise remain legal until the app closes.

    Notes:
     - Queued plaintext segments are held by reference (zero copy). If an upstream handler recycles its buffers after
       `outbound()` returns, copy before enqueueing here.
     - `suppress_ragged_eofs=False` turns an abrupt transport EOF (no close_notify - i.e. possible truncation) into a
       raised SSLError instead of a normal EOF.

    TODO:
     - shutdown timeout: a peer that never answers our close_notify parks us in SHUTTING_DOWN until
       transport EOF; bounding that wait needs a timer facility.
     - context.set_alpn_protocols(['http/1.1'])
     - context.post_handshake_auth = True ?
    """

    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['SslIoPipelineHandler.Config']

        read_chunk_size: int = 64 * 1024

        # Treat an abrupt transport EOF with no close_notify as a normal EOF (like the ssl module's
        # `suppress_ragged_eofs=True`). Strict mode (False) detects truncation attacks but blows up on the very common
        # peers that just drop the connection.
        suppress_ragged_eofs: bool = True

        # Begin the handshake eagerly when an InitialInput is observed (if the core defines one), rather than waiting
        # for the first write or first inbound bytes. Required for client-side use against server-speaks-first protocols
        # (SMTP/IMAP/...), where otherwise nobody ever sends a ClientHello.
        handshake_on_initial_input: bool = True

        # Hysteresis watermarks, in plaintext bytes queued in this handler, for the combined writability signal
        # announced inbound as ReadyForOutput / PauseOutput.
        write_high_watermark: int = 64 * 1024
        write_low_watermark: int = 16 * 1024

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

    # Plaintext accepted from the app but not yet accepted by the SSL engine, flattened into individual memoryview
    # segments. Flattening matters: after SSL_write raises WANT_READ, OpenSSL requires the retry to present the same
    # buffer, so we must always retry exactly the head segment and never re-aggregate or skip ahead.
    _write_q: ta.Deque[memoryview]
    _write_q_bytes = 0

    # Latches / level state. Everything here is either event-driven or re-derived each pump; _emit() is the sole reader
    # that turns them into messages.
    _want_ciphertext = False      # some engine op hit WANT_READ this pump
    _control_activity = False     # engine produced/needed output for its own reasons this turn
    _read_requested = False       # a manual-mode read token from downstream is outstanding
    _read_satisfied = False       # a manual read token was satisfied with data this turn
    _rfi_outstanding = False      # we sent ReadyForInput and haven't received bytes since
    _flush_pending = False        # app requested FlushOutput; not yet forwarded
    _flush_in_seen = False        # transport sent FlushInput; not yet forwarded/swallowed
    _delivered_plaintext = False  # plaintext fed inbound since the last FlushInput we forwarded
    _plaintext_eof = False        # engine reported EOF; synthetic FinalInput owed (once)
    _inbound_eof_sent = False
    _transport_eof = False        # transport FinalInput received; in_bio has been EOF'd
    _close_requested = False      # app FinalOutput received
    _pending_final_output: ta.Any = None
    _final_output_sent = False

    _transport_writable = True  # last transport-side writability signal
    _self_writable = True       # our own queue vs watermarks (hysteresis)
    _announced_writable = True  # last combined value announced inbound

    _in_turn = False
    _dirty = False

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

        self._write_q = collections.deque()

        # Baseline for edge-detection: whatever the transport last told us (pre-TLS writability signals were passed
        # through transparently, so the app has already seen them).
        self._announced_writable = self._transport_writable

        self._state = self.State.NEW
        return self._state

    #

    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        if self.state is None:
            return 0
        # Undelivered = raw records in the BIO plus decrypted bytes parked inside the engine (manual-read mode
        # deliberately leaves data there between read tokens).
        return self._in_bio.pending + self._ssl_obj.pending()

    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        if self.state is None:
            return self._write_q_bytes
        return self._write_q_bytes + self._out_bio.pending

    #

    def _fc(self, ctx: IoPipelineHandlerContext) -> ta.Optional[IoPipelineFlow]:
        return ctx.services.find(IoPipelineFlow)

    def _is_auto_read(self, ctx: IoPipelineHandlerContext) -> bool:
        if (flow := ctx.services.find(IoPipelineFlow)) is None:
            return True
        return flow.is_auto_read()

    ##
    # Phase 1: APPLY - entry points classify, mutate, and call _turn(). Nothing else.

    _INITIAL_INPUT_CLS: ta.ClassVar[ta.Any] = getattr(IoPipelineMessages, 'InitialInput', None)

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.FlushInput):
            if self.state is None:
                ctx.feed_in(msg)
                return
            self._flush_in_seen = True
            self._turn(ctx)
            return

        if isinstance(msg, IoPipelineFlowMessages.ReadyForOutput):
            self._transport_writable = True
            if self.state is None:
                ctx.feed_in(msg)
                return
            self._turn(ctx)  # May unblock queued encryption; combined signal re-announced in _emit.
            return

        if isinstance(msg, IoPipelineFlowMessages.PauseOutput):
            self._transport_writable = False
            if self.state is None:
                ctx.feed_in(msg)
                return
            self._turn(ctx)
            return

        if isinstance(msg, IoPipelineMessages.FinalInput):
            # Transport read-EOF. We own EOF delivery from here on: consume this one, and _emit() will produce exactly
            # one synthetic FinalInput when the *engine* reaches EOF (which, in manual-read mode, may be after later
            # read tokens drain remaining decrypted data - half-close works).
            ctx.mark_propagated('inbound', msg)
            self._ensure_state()
            if not self._transport_eof:
                self._transport_eof = True
                self._in_bio.write_eof()
            self._rfi_outstanding = False
            self._turn(ctx)
            return

        if self._INITIAL_INPUT_CLS is not None and isinstance(msg, self._INITIAL_INPUT_CLS):
            ctx.feed_in(msg)
            if self._config.handshake_on_initial_input:
                # Client side: generates the ClientHello immediately. Server side: leaves the engine in WANT_READ, which
                # in manual-read mode arms the first transport read via _emit().
                self._ensure_state()
                self._turn(ctx)
            return

        if ByteStreamBuffers.can_bytes(msg):
            self._ensure_state()
            if self._transport_eof or self._state == self.State.CLOSED:
                # Stray records after EOF/close (e.g. peer data crossing our teardown on the wire); nothing can be done
                # with them, and the BIO would reject a write after write_eof().
                return
            for seg in ByteStreamBuffers.iter_segments(msg):
                self._in_bio.write(seg)
            self._rfi_outstanding = False  # The outstanding read token (if any) has been honored.
            self._turn(ctx)
            return

        ctx.feed_in(msg)

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.ReadyForInput):
            # Recorded even pre-establishment so the token isn't forgotten across the handshake. _emit() synthesizes our
            # own upstream ReadyForInput iff the engine actually needs wire bytes.
            self._ensure_state()
            self._read_requested = True
            self._turn(ctx)
            return

        if isinstance(msg, IoPipelineFlowMessages.FlushOutput):
            if self.state is None:
                ctx.feed_out(msg)
                return
            self._flush_pending = True
            self._turn(ctx)
            return

        if isinstance(msg, IoPipelineMessages.FinalOutput):
            self._on_outbound_final_output(ctx, msg)
            return

        if ByteStreamBuffers.can_bytes(msg):
            self._on_outbound_bytes(ctx, msg)
            return

        ctx.feed_out(msg)

    def _on_outbound_final_output(self, ctx: IoPipelineHandlerContext, msg: IoPipelineMessages.FinalOutput) -> None:  # noqa
        ctx.mark_propagated('outbound', msg)  # We own its delivery now; released by _emit() once CLOSED.
        if self._close_requested or self._final_output_sent:
            return  # Duplicate close.
        self._ensure_state()
        self._close_requested = True
        self._pending_final_output = msg
        self._turn(ctx)

    def _on_outbound_bytes(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if self._close_requested or self._final_output_sent:
            raise RuntimeError('Write after FinalOutput on SslIoPipelineHandler')
        self._ensure_state()
        if self._state == self.State.CLOSED:
            # Peer-initiated teardown racing an in-flight app write; the app will see FinalInput shortly.
            return
        for seg in ByteStreamBuffers.iter_segments(msg):
            mv = memoryview(seg)
            if mv.nbytes:  # SSL_write of zero bytes is an OpenSSL error.
                self._write_q.append(mv)
                self._write_q_bytes += mv.nbytes
        self._turn(ctx)

    ##
    # Turn driver.

    def _turn(self, ctx: IoPipelineHandlerContext) -> None:
        if self._in_turn:
            # Reentrant event (something we fed synchronously caused a message back into this handler). State is already
            # mutated; let the outer turn pick it up so emissions stay ordered.
            self._dirty = True
            return

        self._in_turn = True
        try:
            while True:
                self._dirty = False
                auto_read = self._is_auto_read(ctx)
                try:
                    in_chunks, out_chunks = self._pump(auto_read)
                except ssl.SSLError:
                    # Poison the machine so later events don't grind a broken engine, then let the error propagate as a
                    # pipeline error. (Any MustPropagate messages we received were already mark_propagated at intake, so
                    # this can't strand one.)
                    self._state = self.State.CLOSED
                    self._write_q.clear()
                    self._write_q_bytes = 0
                    raise
                self._emit(ctx, in_chunks, out_chunks, auto_read)
                if not self._dirty:
                    break
        finally:
            self._in_turn = False

    ##
    # Phase 2: PUMP - advance the SSL machine to quiescence. No ctx access anywhere below here.

    def _pump(self, auto_read: bool) -> ta.Tuple[ta.List[bytes], ta.List[bytes]]:
        in_chunks: ta.List[bytes] = []
        out_chunks: ta.List[bytes] = []

        self._want_ciphertext = False  # Re-derived: every starved engine op below re-asserts it.

        progressed = True
        while progressed:
            progressed = self._step_handshake()
            progressed |= self._step_writes(out_chunks)
            progressed |= self._step_reads(in_chunks, auto_read)
            progressed |= self._step_shutdown()

        self._collect_ciphertext(out_chunks)
        return (in_chunks, out_chunks)

    def _collect_ciphertext(self, out_chunks: ta.List[bytes]) -> bool:
        any_ = False
        while True:
            b = self._out_bio.read()
            if not b:
                break
            out_chunks.append(b)
            any_ = True
        return any_

    def _step_handshake(self) -> bool:
        if self._state == self.State.NEW:
            self._state = self.State.HANDSHAKE
        if self._state != self.State.HANDSHAKE:
            return False

        try:
            self._ssl_obj.do_handshake()

        except ssl.SSLWantReadError:
            self._want_ciphertext = True
            self._control_activity = True  # Any records generated (e.g. ClientHello) are engine-driven.
            return False

        except ssl.SSLWantWriteError:
            # Can't really happen with an unbounded MemoryBIO; records are collected after the pump loop.
            self._control_activity = True
            return False

        except ssl.SSLError:
            if self._transport_eof and self._config.suppress_ragged_eofs:
                # Peer vanished mid-handshake; there is no one left to talk to.
                self._plaintext_eof = True
                self._state = self.State.CLOSED
                return True
            raise

        self._state = self.State.ESTABLISHED
        self._control_activity = True  # Handshake completion may leave records (e.g. session tickets).
        return True

    def _step_writes(self, out_chunks: ta.List[bytes]) -> bool:
        if self._state != self.State.ESTABLISHED:
            # No app data may enter the engine once shutdown has begun; _step_shutdown() refuses to start until this
            # queue is empty, so nothing is stranded.
            return False
        if not self._write_q:
            return False
        if not self._transport_writable and not self._close_requested:
            # Output flow control: hold backpressure here, at the plaintext queue, where byte accounting is honest -
            # once bytes enter the engine they can't be un-sent. Close is exempt: data already accepted from the app
            # must not be stranded behind a paused transport during shutdown.
            return False

        progressed = False
        while self._write_q:
            mv = self._write_q[0]
            try:
                self._ssl_obj.write(mv)

            except ssl.SSLWantReadError:
                # Renegotiation / KeyUpdate: the engine needs peer bytes before accepting more plaintext. CRITICAL: the
                # retry must present exactly this same `mv`, and no later segment may be attempted first - hence
                # head-of-queue discipline and no re-aggregation.
                self._want_ciphertext = True
                self._control_activity = True
                break

            except ssl.SSLWantWriteError:
                # Shouldn't happen with a MemoryBIO; drain and retry, bailing if that made no room.
                if not self._collect_ciphertext(out_chunks):
                    raise
                progressed = True
                continue

            self._write_q.popleft()
            self._write_q_bytes -= mv.nbytes
            progressed = True

        return progressed

    def _step_reads(self, in_chunks: ta.List[bytes], auto_read: bool) -> bool:
        # Reads are only meaningful post-handshake (do_handshake is the consumer before that), and remain legal during
        # SHUTTING_DOWN (the peer may have sent app data before seeing our close_notify). Never touch a CLOSED engine -
        # stray late records must not blow up the pipeline.
        if self._state not in (self.State.ESTABLISHED, self.State.SHUTTING_DOWN):
            return False

        progressed = False
        while not self._plaintext_eof and (auto_read or self._read_requested):
            try:
                b = self._ssl_obj.read(self._config.read_chunk_size)

            except ssl.SSLWantReadError:
                self._want_ciphertext = True
                break

            except ssl.SSLWantWriteError:
                # Renegotiation wants records flushed first.
                self._control_activity = True
                if not self._collect_ciphertext([]):  # pragma: no cover - MemoryBIO shouldn't get here
                    break
                progressed = True
                continue

            except ssl.SSLZeroReturnError:
                # Clean close_notify from the peer. Note we do NOT initiate our own shutdown: writes remain legal
                # (half-close) until the app sends FinalOutput.
                self._plaintext_eof = True
                progressed = True
                break

            except ssl.SSLEOFError:
                if self._config.suppress_ragged_eofs:
                    self._plaintext_eof = True
                    progressed = True
                    break
                raise

            except ssl.SSLError:
                if self._transport_eof and self._config.suppress_ragged_eofs:
                    self._plaintext_eof = True
                    progressed = True
                    break
                raise

            if not b:
                self._plaintext_eof = True
                progressed = True
                break

            in_chunks.append(b)
            progressed = True

            if not auto_read:
                # One-read-per-request: a single delivered chunk satisfies the manual token.
                self._read_requested = False
                self._read_satisfied = True
                break

        return progressed

    def _step_shutdown(self) -> bool:
        if not self._close_requested or self._state == self.State.CLOSED:
            return False

        if self._state in (self.State.NEW, self.State.HANDSHAKE):
            # No (complete) session to shut down gracefully.
            self._state = self.State.CLOSED
            return True

        if self._write_q:
            # Queued plaintext must be encrypted (and any renegotiation it's blocked on completed) before close_notify -
            # close_notify after dropped data is just a politer form of truncation.
            return False

        try:
            self._ssl_obj.unwrap()

        except ssl.SSLWantReadError:
            # Our close_notify is generated (collected after the loop); now waiting on the peer's.
            self._control_activity = True
            self._want_ciphertext = True
            if self._transport_eof:
                # The peer will never answer; our half of the shutdown is out. Don't wedge forever.
                self._state = self.State.CLOSED
                return True
            if self._state != self.State.SHUTTING_DOWN:
                self._state = self.State.SHUTTING_DOWN
                return True
            return False

        except ssl.SSLWantWriteError:
            self._control_activity = True
            if self._state != self.State.SHUTTING_DOWN:
                self._state = self.State.SHUTTING_DOWN
                return True
            return False

        except ssl.SSLError:
            # Peer misbehaved during shutdown or the engine is in a weird state; nothing more can be done gracefully
            # either way.
            self._state = self.State.CLOSED
            self._control_activity = True
            return True

        self._state = self.State.CLOSED
        self._control_activity = True
        return True

    ##
    # Phase 3: EMIT - the only place machine-produced messages are fed. Order matters and is fixed:
    #
    #   1. ciphertext -> out (before plaintext: a reentrant app write's ciphertext must serialize *after* records
    #                         already produced, or TLS record order breaks on the wire)
    #   2. FlushOutput -> out
    #   3. deferred FinalOutput -> out (only once CLOSED; close_notify precedes it)
    #   4. plaintext -> in
    #   5. synthetic FinalInput -> in (exactly once)
    #   6. FlushInput -> in
    #   7. ReadyForInput -> out (deduplicated request for more wire bytes)
    #   8. ReadyForOutput/PauseOutput -> in (combined writability, edge-emitted)

    def _emit(
            self,
            ctx: IoPipelineHandlerContext,
            in_chunks: ta.List[bytes],
            out_chunks: ta.List[bytes],
            auto_read: bool,
    ) -> None:
        fc = self._fc(ctx)

        # 1) Ciphertext.
        for b in out_chunks:
            ctx.feed_out(b)

        # 2) FlushOutput: forward the app's flush once its bytes (if any) have actually gone out; emit our own after
        # engine-driven output (handshake / shutdown / renegotiation records, session tickets) so manual-flush
        # transports never sit on control records.
        produced = bool(out_chunks)
        emit_flush = False
        if self._flush_pending and (produced or not self._write_q):
            self._flush_pending = False
            emit_flush = True
        elif produced and self._control_activity and fc is not None:
            emit_flush = True
        self._control_activity = False
        if emit_flush:
            ctx.feed_out(IoPipelineFlowMessages.FlushOutput())

        # 3) Deferred FinalOutput.
        if self._state == self.State.CLOSED and self._pending_final_output is not None:
            fo = self._pending_final_output
            self._pending_final_output = None
            self._final_output_sent = True
            ctx.feed_out(fo)

        # 4) Plaintext.
        for b in in_chunks:
            self._delivered_plaintext = True
            ctx.feed_in(b)

        # 5) Synthetic FinalInput, exactly once. An EOF also retires any outstanding manual read token - but
        # deliberately does not count as 'delivered' for FlushInput purposes.
        if self._plaintext_eof:
            self._read_requested = False
            if not self._inbound_eof_sent:
                self._inbound_eof_sent = True
                ctx.feed_in(IoPipelineMessages.FinalInput())

        # 6) FlushInput: forwarded when the transport's flush follows plaintext we actually delivered, or synthesized
        # when a manual read was satisfied from internal buffers (no transport flush coming).
        flush_in_seen = self._flush_in_seen
        self._flush_in_seen = False
        read_satisfied = self._read_satisfied
        self._read_satisfied = False
        if self._delivered_plaintext and (flush_in_seen or read_satisfied):
            self._delivered_plaintext = False
            ctx.feed_in(IoPipelineFlowMessages.FlushInput())

        # 7) ReadyForInput: in manual mode, request wire bytes iff the engine is starved (_want_ciphertext) AND someone
        # actually needs progress - the handshake, a pending shutdown, an outstanding app read, or a write blocked on
        # renegotiation. Deduplicated by _rfi_outstanding, which clears when bytes arrive.
        if (
                not auto_read and
                fc is not None and
                self._want_ciphertext and
                not self._rfi_outstanding and
                not self._transport_eof and
                self._state in (self.State.HANDSHAKE, self.State.ESTABLISHED, self.State.SHUTTING_DOWN)
        ):
            if (
                    self._state != self.State.ESTABLISHED or
                    self._read_requested or
                    bool(self._write_q)
            ):
                self._rfi_outstanding = True
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

        # 8) Writability: hysteresis on our own plaintext backlog, combined with the transport's signal, announced
        # inbound only on change.
        if self._self_writable:
            if self._write_q_bytes > self._config.write_high_watermark:
                self._self_writable = False
        elif self._write_q_bytes <= self._config.write_low_watermark:
            self._self_writable = True

        if fc is not None:
            eff = self._transport_writable and self._self_writable
            if eff != self._announced_writable:
                self._announced_writable = eff
                ctx.feed_in(
                    IoPipelineFlowMessages.ReadyForOutput() if eff
                    else IoPipelineFlowMessages.PauseOutput(),
                )
