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
from omlish import logs

from ...config import Config
from ...serving import serve
from .utils import AsgiApp
from .utils import AsgiRecv
from .utils import AsgiScope
from .utils import AsgiSend
from .utils import send_response
from .utils import stub_lifespan


log = logging.getLogger(__name__)


##


class HiAsgiApp(AsgiApp):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        await send_response(send, 200, body=b'hi')


class ByeAsgiApp(AsgiApp):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        await send_response(send, 200, body=b'bye')


##


@dc.dataclass(frozen=True)
class Endpoint:
    method: ta.Literal['GET', 'POST']
    endpoint: str


class InjApp(AsgiApp):
    def __init__(self, endpoints: ta.Mapping[Endpoint, AsgiApp]) -> None:
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
        inj.bind_map_provider(ta.Mapping[Endpoint, AsgiApp]),
        inj.singleton(InjApp),

        inj.singleton(HiAsgiApp),
        inj.MapBinding(inj.Key(ta.Mapping[Endpoint, AsgiApp]), Endpoint('GET', '/hi'), inj.Key(HiAsgiApp)),

        inj.singleton(ByeAsgiApp),
        inj.MapBinding(inj.Key(ta.Mapping[Endpoint, AsgiApp]), Endpoint('GET', '/bye'), inj.Key(ByeAsgiApp)),
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
