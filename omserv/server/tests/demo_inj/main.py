"""
TODO:
 - remember - just a second cookie lol
 - chrome save text boxes / login

https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import dataclasses as dc
import logging
import typing as ta

import anyio

from omlish import inject as inj
from omlish.http.asgi import AsgiApp_
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import send_response
from omlish.http.asgi import stub_lifespan
from omlish.logs import all as logs

from ...config import Config
from ...default import serve


log = logging.getLogger(__name__)


##


class HiAsgiApp(AsgiApp_):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        await send_response(send, 200, body=b'hi')


class ByeAsgiApp(AsgiApp_):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        await send_response(send, 200, body=b'bye')


##


@dc.dataclass(frozen=True)
class Endpoint:
    method: ta.Literal['GET', 'POST']
    endpoint: str


class InjApp(AsgiApp_):
    def __init__(self, endpoints: ta.Mapping[Endpoint, AsgiApp_]) -> None:
        super().__init__()
        self._endpoints = endpoints

    async def __call__(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        match scope_ty := scope['type']:
            case 'lifespan':
                await stub_lifespan(scope, recv, send)
                return

            case 'http':
                ep = Endpoint(scope['method'], scope['raw_path'].decode())
                app = self._endpoints.get(ep)
                if app is None:
                    await send_response(send, 404)
                    return

                await app(scope, recv, send)

            case _:
                raise ValueError(f'Unhandled scope type: {scope_ty!r}')


##


def _bind() -> inj.Elements:
    return inj.as_elements(
        inj.map_binder[Endpoint, AsgiApp_](),
        inj.bind(InjApp, singleton=True),

        inj.bind(HiAsgiApp, singleton=True),
        inj.map_binder[Endpoint, AsgiApp_]().bind(Endpoint('GET', '/hi'), HiAsgiApp),

        inj.bind(ByeAsgiApp, singleton=True),
        inj.map_binder[Endpoint, AsgiApp_]().bind(Endpoint('GET', '/bye'), ByeAsgiApp),
    )


def _main() -> None:
    logs.configure_standard_logging(logging.INFO)

    async def _a_main():
        injector = inj.create_injector(_bind())
        await serve(
            injector[InjApp],
            Config(),
            handle_shutdown_signals=True,
        )

    anyio.run(_a_main)


if __name__ == '__main__':
    _main()
