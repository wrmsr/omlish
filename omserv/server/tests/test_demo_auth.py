import contextlib
import functools

import anyio
import httpx
import pytest

from ..config import Config
from ..types import AsgiWrapper
from ..workers import worker_serve
from .demo_auth.main import auth_app
from .sanity import sanity_framework
from .utils import TIMEOUT_S
from .utils import get_free_port
from .utils import headers_time_patch  # noqa
from omlish import lang


@pytest.mark.trio
async def test_demo_auth():
    port = get_free_port()
    sev = anyio.Event()

    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            aes.enter_context(lang.defer(sev.set))

            async with httpx.AsyncClient() as client:
                tt = lang.timeout(TIMEOUT_S)
                while True:
                    tt()
                    try:
                        r = await client.get(f'https://localhost:/{port}')
                    except httpx.ConnectError:
                        await anyio.sleep(.1)
                        continue
                    break

                print(r)

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            worker_serve,
            AsgiWrapper(auth_app),
            Config(
                bind=(f'127.0.0.1:{port}',),
            ),
            shutdown_trigger=sev.wait,
        ))
        tg.start_soon(inner)
