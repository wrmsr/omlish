# ruff: noqa: UP006 UP007 UP045
# @om-lite
import base64
import hashlib
import os
import typing as ta

from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from ....lite.check import check
from ....lite.namespaces import NamespaceClass
from ...headers import HttpHeaders
from ..clients.requests import IoPipelineHttpRequestEncoder
from ..clients.responses import IoPipelineHttpResponseDecoder
from ..requests import FullIoPipelineHttpRequest
from ..requests import IoPipelineHttpRequestEnd
from ..requests import IoPipelineHttpRequestHead
from ..responses import FullIoPipelineHttpResponse
from ..responses import IoPipelineHttpResponseHead
from ..servers.requests import IoPipelineHttpRequestDecoder
from ..servers.responses import IoPipelineHttpResponseEncoder
from .objects import IoPipelineWebsocketOpen


##


class IoPipelineWebsocketHandshakes(NamespaceClass):
    WS_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    @classmethod
    def compute_accept_for_key(cls, key_b64: str) -> str:
        s = (key_b64 + cls.WS_GUID).encode('ascii')
        d = hashlib.sha1(s).digest()  # noqa
        return base64.b64encode(d).decode('ascii')


class IoPipelineWebsocketServerUpgradeHandler(IoPipelineHandler):
    """
    Detects and accepts an HTTP/1.1 Websocket Upgrade request, responds with 101, and emits WsOpen. After upgrade,
    passes through subsequent messages unchanged.
    """

    def __init__(
            self,
            *,
            subprotocols: ta.Sequence[str] = (),
    ) -> None:
        super().__init__()

        self._subprotocols = subprotocols

    _upgraded: bool = False

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if self._upgraded:
            if isinstance(msg, IoPipelineHttpRequestEnd):
                return
            ctx.feed_in(msg)
            return

        if isinstance(msg, IoPipelineHttpRequestHead):
            if not self._is_ws_upgrade_request(msg.headers):
                ctx.feed_in(msg)
                return

            key = msg.headers.single.get('Sec-Websocket-Key')

            accept = IoPipelineWebsocketHandshakes.compute_accept_for_key(check.not_none(key))

            chosen_proto: ta.Optional[str] = None
            if self._subprotocols:
                # Simple selection: first matching requested subprotocol (if present)
                req_subp = msg.headers.single.get('Sec-Websocket-Protocol')
                if req_subp is not None:
                    requested = [s.strip() for s in req_subp.split(',')]
                    for s in requested:
                        if s in self._subprotocols:
                            chosen_proto = s
                            break

            hdrs = HttpHeaders.of(None).update(
                ('Upgrade', 'websocket'),
                ('Connection', 'Upgrade'),
                ('Sec-Websocket-Accept', accept),
                ('Sec-Websocket-Protocol', chosen_proto) if chosen_proto else ('', None),  # ignored
                if_present='skip',
            )

            resp = IoPipelineHttpResponseHead(
                status=101,
                reason='Switching Protocols',
                headers=hdrs,
            )
            ctx.feed_out(resp)

            self._upgraded = True
            ctx.defer_no_context(lambda: self._remove_http_handlers(ctx))
            ctx.feed_in(IoPipelineWebsocketOpen(subprotocol=chosen_proto))
            return

        elif isinstance(msg, FullIoPipelineHttpRequest):
            # If a handler up the chain aggregates into Full, treat the same as head
            self.inbound(ctx, msg.head)
            return

        ctx.feed_in(msg)

    def _is_ws_upgrade_request(self, headers: HttpHeaders) -> bool:
        if not headers.contains_value('Upgrade', 'websocket', ignore_case=True):
            return False
        if not headers.contains_value('Connection', 'upgrade', ignore_case=True):
            return False
        ver = headers.single.get('Sec-Websocket-Version')
        if ver != '13':
            return False
        if headers.single.get('Sec-Websocket-Key') is None:
            return False
        return True

    def _remove_http_handlers(self, ctx: IoPipelineHandlerContext) -> None:
        for ty in (
                IoPipelineHttpRequestDecoder,
                IoPipelineHttpResponseEncoder,
        ):
            for ref in ctx.pipeline.find_handlers_of_type(ty):
                ctx.pipeline.remove(ref)


class IoPipelineWebsocketClientUpgradeHandler(IoPipelineHandler):
    """
    Injects required headers in outbound HTTP request for Websocket upgrade. Validates 101 response inbound and emits
    WsOpen.
    """

    def __init__(
            self,
            *,
            host: str,
            subprotocols: ta.Sequence[str] = (),
    ) -> None:
        super().__init__()

        self._host = host
        self._subprotocols = subprotocols

    _key_b64: ta.Optional[str] = None
    _upgraded: bool = False

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if self._upgraded:
            ctx.feed_out(msg)
            return

        if isinstance(msg, IoPipelineHttpRequestHead):
            ctx.feed_out(self._with_ws_upgrade_headers(msg))
            return

        elif isinstance(msg, FullIoPipelineHttpRequest):
            new_head = self._with_ws_upgrade_headers(msg.head)
            ctx.feed_out(FullIoPipelineHttpRequest(head=new_head, body=msg.body))
            return

        ctx.feed_out(msg)

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if self._upgraded:
            ctx.feed_in(msg)
            return

        if isinstance(msg, IoPipelineHttpResponseHead):
            if msg.status != 101:
                ctx.feed_in(msg)
                return

            check.state(self._key_b64 is not None)
            accept = msg.headers.single.get('Sec-Websocket-Accept')
            check.not_none(accept)
            check.equal(accept, IoPipelineWebsocketHandshakes.compute_accept_for_key(self._key_b64))  # type: ignore[arg-type]  # noqa

            chosen_proto = msg.headers.single.get('Sec-Websocket-Protocol')

            self._upgraded = True
            ctx.defer_no_context(lambda: self._remove_http_handlers(ctx))
            ctx.feed_in(IoPipelineWebsocketOpen(subprotocol=chosen_proto))
            return

        elif isinstance(msg, FullIoPipelineHttpResponse):
            self.inbound(ctx, msg.head)
            return

        ctx.feed_in(msg)

    def _with_ws_upgrade_headers(self, head: IoPipelineHttpRequestHead) -> IoPipelineHttpRequestHead:
        # Generate a new random key
        key = base64.b64encode(os.urandom(16)).decode('ascii')
        self._key_b64 = key

        hdrs = HttpHeaders.of(head.headers).update(
            ('Host', self._host),
            ('Upgrade', 'websocket'),
            ('Connection', 'Upgrade'),
            ('Sec-Websocket-Version', '13'),
            ('Sec-Websocket-Key', key),
            ('Sec-Websocket-Protocol', ', '.join(self._subprotocols)) if self._subprotocols else ('', None),
            if_present='skip',
        )

        return IoPipelineHttpRequestHead(
            method=head.method,
            target=head.target,
            headers=hdrs,
            parsed=head.parsed,
            version=head.version,
        )

    def _remove_http_handlers(self, ctx: IoPipelineHandlerContext) -> None:
        for ty in (
                IoPipelineHttpResponseDecoder,
                IoPipelineHttpRequestEncoder,
        ):
            for ref in ctx.pipeline.find_handlers_of_type(ty):
                ctx.pipeline.remove(ref)
