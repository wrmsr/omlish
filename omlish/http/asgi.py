import abc
import logging
import typing as ta
import urllib.parse

from .. import check
from . import consts


log = logging.getLogger(__name__)


##


AsgiScope: ta.TypeAlias = ta.Mapping[str, ta.Any]
AsgiMessage: ta.TypeAlias = ta.Mapping[str, ta.Any]
AsgiRecv: ta.TypeAlias = ta.Callable[[], ta.Awaitable[AsgiMessage]]
AsgiSend: ta.TypeAlias = ta.Callable[[AsgiMessage], ta.Awaitable[None]]
AsgiApp: ta.TypeAlias = ta.Callable[[AsgiScope, AsgiRecv, AsgiSend], ta.Awaitable[None]]


class AbstractAsgiApp(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        raise NotImplementedError


##


async def stub_lifespan(scope: AsgiScope, recv: AsgiRecv, send: AsgiSend, *, verbose: bool = False) -> None:
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
        send: AsgiSend,
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
        send: AsgiSend,
        body: bytes = b'',
) -> None:
    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def send_response(
        send: AsgiSend,
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
        send: AsgiSend,
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


async def read_body(recv: AsgiRecv) -> bytes:
    body = b''
    more_body = True
    while more_body:
        message = await recv()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body


async def read_form_body(recv: AsgiRecv) -> dict[bytes, bytes]:
    body = await read_body(recv)
    dct = urllib.parse.parse_qs(body)  # noqa
    return {k: check.single(v) for k, v in dct.items()}
