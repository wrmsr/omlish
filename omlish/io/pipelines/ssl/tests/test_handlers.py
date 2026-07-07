import ssl
import typing as ta
import unittest

from .....secrets import tempssl
from ...core import IoPipelineMessages
from ...flow.stub import StubIoPipelineFlowService
from ...flow.types import IoPipelineFlow
from ...flow.types import IoPipelineFlowMessages
from ..handlers import SslIoPipelineHandler


class Services:
    def __init__(self, flow=None):
        self._flow = flow

    def find(self, cls):
        if cls is IoPipelineFlow and self._flow is not None:
            return self._flow
        return None


class Ctx:
    """Fake IoPipelineHandlerContext: feed_in -> app side, feed_out -> transport side."""

    def __init__(self, name, flow=None):
        self.name = name
        self.services = Services(flow)
        self.app_msgs = []  # what the app above received
        self.transport: ta.Any = None  # FakeTransport below
        self.propagated = []
        self.on_app: ta.Any = None

    def feed_in(self, msg):
        self.app_msgs.append(msg)
        if self.on_app is not None:
            self.on_app(msg)

    def feed_out(self, msg):
        self.transport.from_handler(msg)

    def mark_propagated(self, direction, msg):
        self.propagated.append((direction, msg))


class FakeTransport:
    """
    Sits below the handler. In manual mode, inbound bytes are only delivered against a ReadyForInput token, followed by
    a FlushInput (mirroring the real transport contract).
    """

    def __init__(self, name, handler, ctx, manual=False):
        self.name = name
        self.handler = handler
        self.ctx = ctx
        self.manual = manual
        self.peer = None
        self.wire_out = []  # everything the handler fed out (for assertions)
        self.rx_q = []  # bytes received from peer, awaiting delivery (manual mode)
        self.read_armed = not manual
        self.eof_pending = False
        self.eof_delivered = False
        self.closed_write = False

    # messages coming DOWN from the handler:

    def from_handler(self, msg):
        self.wire_out.append(msg)
        if isinstance(msg, IoPipelineFlowMessages.ReadyForInput):
            self.read_armed = True
            self._maybe_deliver()
        elif isinstance(msg, IoPipelineFlowMessages.FlushOutput):
            pass
        elif isinstance(msg, IoPipelineMessages.FinalOutput):
            self.closed_write = True
            if self.peer is not None:
                self.peer.on_peer_eof()
        elif isinstance(msg, (bytes, bytearray, memoryview)):
            assert not self.closed_write, f'{self.name}: bytes after FinalOutput!'
            if self.peer is not None:
                self.peer.on_peer_bytes(bytes(msg))
        # else: ignore

    # events coming from the wire:

    def on_peer_bytes(self, b):
        self.rx_q.append(b)
        self._maybe_deliver()

    def on_peer_eof(self):
        self.eof_pending = True
        self._maybe_deliver()

    def _maybe_deliver(self):
        while self.rx_q and (self.read_armed or not self.manual):
            b = self.rx_q.pop(0)
            if self.manual:
                self.read_armed = False
            self.handler.inbound(self.ctx, b)
            self.handler.inbound(self.ctx, IoPipelineFlowMessages.FlushInput())
        if self.eof_pending and not self.rx_q and not self.eof_delivered:
            self.eof_delivered = True
            self.handler.inbound(self.ctx, IoPipelineMessages.FinalInput())


def make_pair(
        cert: tempssl.SslCert,
        *,
        client_auto=True,
        server_auto=True,
        client_flow=True,
        server_flow=True,
):
    server_ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_ssl_ctx.load_cert_chain(cert.cert_file, cert.key_file)
    client_ssl_ctx = ssl.create_default_context(cafile=cert.cert_file)

    ch = SslIoPipelineHandler(client_ssl_ctx, server_side=False, server_hostname='localhost')
    sh = SslIoPipelineHandler(server_ssl_ctx, server_side=True)

    cctx = Ctx('client', StubIoPipelineFlowService(auto_read=client_auto) if client_flow else None)
    sctx = Ctx('server', StubIoPipelineFlowService(auto_read=server_auto) if server_flow else None)

    ct = FakeTransport('client', ch, cctx, manual=not client_auto)
    st = FakeTransport('server', sh, sctx, manual=not server_auto)
    cctx.transport = ct
    sctx.transport = st
    ct.peer = st
    st.peer = ct
    return ch, sh, cctx, sctx, ct, st


def app_bytes(ctx):
    return b''.join(bytes(m) for m in ctx.app_msgs if isinstance(m, (bytes, bytearray, memoryview)))


def has(ctx_or_list, cls):
    msgs = ctx_or_list.app_msgs if isinstance(ctx_or_list, Ctx) else ctx_or_list
    return any(isinstance(m, cls) for m in msgs)


class TestSslHandlers(unittest.TestCase):
    _cert: ta.ClassVar[tempssl.SslCert]

    @classmethod
    def setUpClass(cls):
        from .....subprocesses import sync as _  # import side-effect installing _DEFAULT_SUBPROCESSES  # noqa

        cls._cert = tempssl.generate_temp_localhost_ssl_cert().cert

    def test_auto_read_echo(self):
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert)
        ch.outbound(cctx, b'hello over tls')  # kicks handshake, queues plaintext
        ch.outbound(cctx, IoPipelineFlowMessages.FlushOutput())
        assert app_bytes(sctx) == b'hello over tls', app_bytes(sctx)
        assert ch.state == SslIoPipelineHandler.State.ESTABLISHED
        assert sh.state == SslIoPipelineHandler.State.ESTABLISHED
        sh.outbound(sctx, b'echo!')
        sh.outbound(sctx, IoPipelineFlowMessages.FlushOutput())
        assert app_bytes(cctx) == b'echo!', app_bytes(cctx)
        # accounting sane:
        assert ch.outbound_buffered_bytes() == 0 and sh.outbound_buffered_bytes() == 0

    def test_initial_input_client_handshake(self):
        # Server-speaks-first protocol: app never writes first; InitialInput must kick the ClientHello.
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert)
        ch.inbound(cctx, IoPipelineMessages.InitialInput())
        assert ch.state == SslIoPipelineHandler.State.ESTABLISHED, ch.state
        sh.outbound(sctx, b'220 smtp greeting')
        assert app_bytes(cctx) == b'220 smtp greeting'

    def test_manual_read_server(self):
        # Server in manual-read mode: multi-flight handshake must self-arm transport reads.
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert, server_auto=False)
        # Server-side manual flow: transport needs an initial arm; InitialInput does it.
        sh.inbound(sctx, IoPipelineMessages.InitialInput())
        ch.outbound(cctx, b'request')
        ch.outbound(cctx, IoPipelineFlowMessages.FlushOutput())
        assert sh.state == SslIoPipelineHandler.State.ESTABLISHED, sh.state
        # No app read requested yet: plaintext must be parked, not delivered.
        assert app_bytes(sctx) == b'', sctx.app_msgs
        assert sh.inbound_buffered_bytes() > 0
        # App asks for one read:
        sh.outbound(sctx, IoPipelineFlowMessages.ReadyForInput())
        assert app_bytes(sctx) == b'request', sctx.app_msgs
        assert has(sctx, IoPipelineFlowMessages.FlushInput)

    def test_graceful_shutdown(self):
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert)
        ch.outbound(cctx, b'bye soon')
        assert app_bytes(sctx) == b'bye soon'
        ch.outbound(cctx, IoPipelineFlowMessages.FlushOutput())
        ch.outbound(cctx, IoPipelineMessages.FinalOutput())
        # Server sees clean EOF:
        assert has(sctx, IoPipelineMessages.FinalInput), sctx.app_msgs
        # Server closes its side too:
        sh.outbound(sctx, IoPipelineMessages.FinalOutput())
        assert has(cctx, IoPipelineMessages.FinalInput), cctx.app_msgs
        assert ch.state == SslIoPipelineHandler.State.CLOSED, ch.state
        assert sh.state == SslIoPipelineHandler.State.CLOSED, sh.state
        # FinalOutputs released to both transports, exactly once:
        assert sum(isinstance(m, IoPipelineMessages.FinalOutput) for m in ct.wire_out) == 1
        assert sum(isinstance(m, IoPipelineMessages.FinalOutput) for m in st.wire_out) == 1
        # close_notify records must precede FinalOutput on the wire:
        fo_ix = next(i for i, m in enumerate(ct.wire_out) if isinstance(m, IoPipelineMessages.FinalOutput))
        assert any(isinstance(m, bytes) for m in ct.wire_out[:fo_ix])

    def test_half_close_server_keeps_writing(self):
        # Client closes write side; server must still be able to send, client still receive.
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert)
        ch.outbound(cctx, b'req')
        assert app_bytes(sctx) == b'req'
        ch.outbound(cctx, IoPipelineMessages.FinalOutput())
        assert has(sctx, IoPipelineMessages.FinalInput)
        sh.outbound(sctx, b'late response')  # write after peer close_notify: legal half-close
        sh.outbound(sctx, IoPipelineFlowMessages.FlushOutput())
        assert app_bytes(cctx) == b'late response', cctx.app_msgs

    def test_ragged_eof_suppressed(self):
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert)
        ch.outbound(cctx, b'x')
        assert app_bytes(sctx) == b'x'
        # Abrupt transport EOF at the server, no close_notify. The peer is gone: sever the wire so any alert the engine
        # emits toward the dead transport isn't looped back.
        st.peer = None
        sh.inbound(sctx, IoPipelineMessages.FinalInput())
        assert has(sctx, IoPipelineMessages.FinalInput), sctx.app_msgs
        assert sum(isinstance(m, IoPipelineMessages.FinalInput) for m in sctx.app_msgs) == 1
        # And the transport's own FinalInput was consumed:
        assert any(d == 'inbound' for d, _ in sctx.propagated)

    def test_ragged_eof_strict(self):
        cfg = SslIoPipelineHandler.Config(suppress_ragged_eofs=False)
        server_ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_ssl_ctx.load_cert_chain(self._cert.cert_file, self._cert.key_file)
        client_ssl_ctx = ssl.create_default_context(cafile=self._cert.cert_file)
        ch = SslIoPipelineHandler(client_ssl_ctx, server_side=False, server_hostname='localhost')
        sh = SslIoPipelineHandler(server_ssl_ctx, server_side=True, config=cfg)
        cctx: ta.Any = Ctx('client', StubIoPipelineFlowService(auto_read=True))
        sctx: ta.Any = Ctx('server', StubIoPipelineFlowService(auto_read=True))
        ct, st = FakeTransport('client', ch, cctx), FakeTransport('server', sh, sctx)
        cctx.transport, sctx.transport = ct, st
        ct.peer, st.peer = st, ct
        ch.outbound(cctx, b'x')
        st.peer = None
        try:
            sh.inbound(sctx, IoPipelineMessages.FinalInput())
        except ssl.SSLError:
            pass
        else:
            raise AssertionError('strict mode should raise on truncation')
        # FinalInput was consumed before the raise - no dangling MustPropagate:
        assert any(d == 'inbound' for d, _ in sctx.propagated)
        assert sh.state == SslIoPipelineHandler.State.CLOSED

    def test_writability(self):
        cfg = SslIoPipelineHandler.Config(write_high_watermark=1000, write_low_watermark=100)
        server_ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_ssl_ctx.load_cert_chain(self._cert.cert_file, self._cert.key_file)
        client_ssl_ctx = ssl.create_default_context(cafile=self._cert.cert_file)
        ch = SslIoPipelineHandler(client_ssl_ctx, server_side=False, server_hostname='localhost', config=cfg)
        sh = SslIoPipelineHandler(server_ssl_ctx, server_side=True)
        cctx: ta.Any = Ctx('client', StubIoPipelineFlowService(auto_read=True))
        sctx: ta.Any = Ctx('server', StubIoPipelineFlowService(auto_read=True))
        ct, st = FakeTransport('client', ch, cctx), FakeTransport('server', sh, sctx)
        cctx.transport, sctx.transport = ct, st
        ct.peer, st.peer = st, ct

        ch.outbound(cctx, b'warmup')  # establish
        assert app_bytes(sctx) == b'warmup'

        # Transport announces it's stuffed:
        ch.inbound(cctx, IoPipelineFlowMessages.PauseOutput())
        assert has(cctx, IoPipelineFlowMessages.PauseOutput), 'pause should propagate to app'
        n_wire = len(ct.wire_out)
        ch.outbound(cctx, b'z' * 5000)
        assert len(ct.wire_out) == n_wire, 'app data must not be encrypted while unwritable'
        assert ch.outbound_buffered_bytes() == 5000

        # Transport drains:
        ch.inbound(cctx, IoPipelineFlowMessages.ReadyForOutput())
        assert app_bytes(sctx) == b'warmup' + b'z' * 5000
        assert ch.outbound_buffered_bytes() == 0
        assert isinstance(cctx.app_msgs[-1], IoPipelineFlowMessages.ReadyForOutput), cctx.app_msgs[-1]
        # Exactly one pause + one ready announced (edge-triggered, no repeats):
        assert sum(isinstance(m, IoPipelineFlowMessages.PauseOutput) for m in cctx.app_msgs) == 1
        assert sum(isinstance(m, IoPipelineFlowMessages.ReadyForOutput) for m in cctx.app_msgs) == 1

        # Self-induced: pause transport, exceed our own high watermark -> our own backlog must also pause the app even
        # after transport says ready... (transport ready but queue drained instantly here, so instead check the
        # combined-signal path: pause, big write, ready -> drains -> single ReadyForOutput again)

    def test_no_write_reordering_manual_flush(self):
        # FlushOutput arriving while nothing is pending should still pass through.
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert)
        ch.outbound(cctx, b'a')
        n = sum(isinstance(m, IoPipelineFlowMessages.FlushOutput) for m in ct.wire_out)
        ch.outbound(cctx, IoPipelineFlowMessages.FlushOutput())
        assert sum(isinstance(m, IoPipelineFlowMessages.FlushOutput) for m in ct.wire_out) == n + 1

    def test_manual_read_client_and_server(self):
        # Both sides manual: the full handshake must complete purely on self-armed reads.
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert, client_auto=False, server_auto=False)
        sh.inbound(sctx, IoPipelineMessages.InitialInput())
        ch.outbound(cctx, b'ping')
        ch.outbound(cctx, IoPipelineFlowMessages.FlushOutput())
        assert ch.state == SslIoPipelineHandler.State.ESTABLISHED, ch.state
        assert sh.state == SslIoPipelineHandler.State.ESTABLISHED, sh.state
        sh.outbound(sctx, IoPipelineFlowMessages.ReadyForInput())
        assert app_bytes(sctx) == b'ping', sctx.app_msgs
        sh.outbound(sctx, b'pong')
        sh.outbound(sctx, IoPipelineFlowMessages.FlushOutput())
        ch.outbound(cctx, IoPipelineFlowMessages.ReadyForInput())
        assert app_bytes(cctx) == b'pong', cctx.app_msgs

    def test_late_stray_bytes_after_close(self):
        cctx: ta.Any
        sctx: ta.Any
        ch, sh, cctx, sctx, ct, st = make_pair(self._cert)
        ch.outbound(cctx, b'x')
        ch.outbound(cctx, IoPipelineMessages.FinalOutput())
        sh.outbound(sctx, IoPipelineMessages.FinalOutput())
        assert ch.state == SslIoPipelineHandler.State.CLOSED
        # Stray bytes arriving after CLOSED must be ignored, not raise:
        ch.inbound(cctx, b'\x17\x03\x03\x00\x05hello')
