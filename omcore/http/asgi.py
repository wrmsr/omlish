import abc
import typing as ta
import urllib.parse

from .. import check
from .. import lang
from ..logs import all as logs
from . import consts


log = logs.get_module_logger(globals())


##


Scope: ta.TypeAlias = ta.Mapping[str, ta.Any]
Message: ta.TypeAlias = ta.Mapping[str, ta.Any]
Recv: ta.TypeAlias = ta.Callable[[], ta.Awaitable[Message]]
Send: ta.TypeAlias = ta.Callable[[Message], ta.Awaitable[None]]
App: ta.TypeAlias = ta.Callable[[Scope, Recv, Send], ta.Awaitable[None]]
Wrapper: ta.TypeAlias = ta.Callable[[App, Scope, Recv, Send], ta.Awaitable[None]]


class App_(lang.Abstract):  # noqa
    @abc.abstractmethod
    async def __call__(self, scope: Scope, recv: Recv, send: Send) -> None:
        raise NotImplementedError


##


async def stub_lifespan(scope: Scope, recv: Recv, send: Send, *, verbose: bool = False) -> None:
    while True:
        message = await recv()
        if message['type'] == 'lifespan.startup':
            if verbose:
                log.info('Lifespan starting up')
            await send({'type': 'lifespan.startup.complete'})

        elif message['type'] == 'lifespan.shutdown':
            if verbose:
                log.info('Lifespan shutting down')
            await send({'type': 'lifespan.shutdown.complete'})
            return


##


async def start_response(
        send: Send,
        status: int,
        content_type: bytes = consts.CONTENT_TYPE_TEXT_UTF8,
        headers: ta.Sequence[tuple[bytes, bytes]] | None = None,
) -> None:
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', content_type),
            *(headers or ()),
        ],
    })


async def finish_response(
        send: Send,
        body: bytes = b'',
) -> None:
    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def send_response(
        send: Send,
        status: int,
        content_type: bytes = consts.CONTENT_TYPE_TEXT_UTF8,
        headers: ta.Sequence[tuple[bytes, bytes]] | None = None,
        body: bytes = b'',
) -> None:
    await start_response(
        send,
        status=status,
        content_type=content_type, headers=headers,
    )
    await finish_response(
        send,
        body=body,
    )


async def redirect_response(
        send: Send,
        url: str,
        headers: ta.Sequence[tuple[bytes, bytes]] | None = None,
) -> None:
    log.info('Redirecting to %s', url)
    await send({
        'type': 'http.response.start',
        'status': 302,
        'headers': [
            (b'content-type', consts.CONTENT_TYPE_TEXT_UTF8),
            (b'location', url.encode()),
            *(headers or ()),
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': b'',
    })


##


async def read_body(recv: Recv) -> bytes:
    body = b''
    more_body = True
    while more_body:
        message = await recv()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body


async def read_form_body(recv: Recv) -> dict[bytes, bytes]:
    body = await read_body(recv)
    dct = urllib.parse.parse_qs(body)  # noqa
    return {k: check.single(v) for k, v in dct.items()}
