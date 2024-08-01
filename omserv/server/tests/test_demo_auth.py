import contextlib
import functools
import os
import urllib.parse

import anyio
import httpx
import pytest

from omlish import lang

from ..config import Config
from ..types import AsgiWrapper
from ..workers import worker_serve
from .demo_auth.main import auth_app
from .utils import TIMEOUT_S
from .utils import get_free_port
from .utils import headers_time_patch  # noqa


@pytest.mark.trio
async def test_demo_auth():
    # from omlish import logs  # noqa
    # logs.configure_standard_logging('INFO')  # noqa

    port = get_free_port()
    base_url = f'http://127.0.0.1:{port}/'

    os.environ['BASE_SERVER_URL'] = base_url

    sev = anyio.Event()

    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            aes.enter_context(lang.defer(sev.set))

            async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
                tt = lang.timeout(TIMEOUT_S)
                while True:
                    tt()
                    try:
                        r = await client.get(base_url)
                    except httpx.ConnectError:
                        await anyio.sleep(.1)
                        continue
                    break

                assert r.status_code == 200

                r = await client.get(base_url + 'signup')
                assert r.status_code == 200

                email = 'foo@bar.com'
                name = 'foo'
                password = 'barf'

                r = await client.post(
                    base_url + 'signup',
                    content=urllib.parse.urlencode({
                        'email': email,
                        'name': name,
                        'password': password,
                    }),
                )
                assert r.status_code == 302

                r = await client.send(r.next_request)
                assert r.status_code == 200

                print(r)

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            worker_serve,
            AsgiWrapper(auth_app),  # type: ignore
            Config(
                bind=(f'127.0.0.1:{port}',),
            ),
            shutdown_trigger=sev.wait,
        ))
        tg.start_soon(inner)
