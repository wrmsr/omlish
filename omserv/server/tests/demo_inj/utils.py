import abc
import logging
import typing as ta

from omlish import http as hu


log = logging.getLogger(__name__)


AsgiScope: ta.TypeAlias = ta.Mapping[str, ta.Any]
AsgiMessage: ta.TypeAlias = ta.Mapping[str, ta.Any]
AsgiRecv: ta.TypeAlias = ta.Callable[[], ta.Awaitable[AsgiMessage]]
AsgiSend: ta.TypeAlias = ta.Callable[[AsgiMessage], ta.Awaitable[None]]


class AsgiApp(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        raise NotImplementedError


async def stub_lifespan(scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    while True:
        message = await recv()
        if message['type'] == 'lifespan.startup':
            log.info('Lifespan starting up')
            await send({'type': 'lifespan.startup.complete'})

        elif message['type'] == 'lifespan.shutdown':
            log.info('Lifespan shutting down')
            await send({'type': 'lifespan.shutdown.complete'})
            return


async def start_response(
        send: AsgiSend,
        status: int,
        content_type: bytes = hu.consts.CONTENT_TYPE_TEXT_UTF8,
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
        content_type: bytes = hu.consts.CONTENT_TYPE_TEXT_UTF8,
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
