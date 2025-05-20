import contextlib
import functools

import anyio
import httpx
import pytest

from omlish import lang
from omlish.asyncs import all as au
from omlish.sockets.ports import get_available_port

from ...server.config import Config
from ...server.default import serve
from ...server.tests.utils import get_timeout_s
from ...server.tests.utils import headers_time_patch  # noqa
from ...server.types import AsgiWrapper
from .foo import build_foo_app


@pytest.mark.integration
@pytest.mark.asyncs(
    'asyncio',
    'trio',
    # 'trio_asyncio',
)
@au.with_adapter_loop(wait=True)
async def test_foo():
    port = get_available_port()
    server_bind = f'127.0.0.1:{port}'
    base_url = f'http://{server_bind}/'

    sev = anyio.Event()

    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            aes.enter_context(lang.defer(sev.set))  # noqa

            r: httpx.Response
            async with httpx.AsyncClient(timeout=get_timeout_s()) as client:
                tt = lang.Timeout.of(get_timeout_s())
                while True:
                    tt()
                    try:
                        r = await client.get(base_url)
                    except httpx.ConnectError:
                        await anyio.sleep(.1)
                        continue
                    break

                assert r.status_code == 200

                ##

                r = await client.get(base_url + 'foo')
                assert r.status_code == 200

    app = build_foo_app()

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            serve,
            AsgiWrapper(app),
            Config(
                bind=(server_bind,),
            ),
            shutdown_trigger=sev.wait,
        ))

        tg.start_soon(inner)
