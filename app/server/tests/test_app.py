import contextlib
import functools
import json
import secrets
import urllib.parse

import anyio
import httpx
import pytest

from omlish import check
from omlish import inject as inj
from omlish import lang
from omlish.asyncs import all as au
from omlish.http import asgi
from omlish.testing import pytest as ptu
from omserv.server.config import Config
from omserv.server.default import serve
from omserv.server.tests.utils import get_free_port
from omserv.server.tests.utils import get_timeout_s
from omserv.server.tests.utils import headers_time_patch  # noqa
from omserv.server.types import AsgiWrapper

from ...dbs import bind_dbs
from ...secrets import bind_secrets
from ..inject import bind_app
from ..inject import bind_in_memory_user_store


def randhex(l: int) -> str:
    return hex(secrets.randbits(4 * l))[2:]


@pytest.mark.integration
@ptu.skip.if_cant_import('greenlet')
@pytest.mark.asyncs(
    'asyncio',
    'trio',
    # 'trio_asyncio',
)
@au.with_adapter_loop(wait=True)
async def test_auth(harness):
    # from omlish import logs  # noqa
    # logs.configure_standard_logging('DEBUG')  # noqa

    port = get_free_port()
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

                r = await client.get(base_url + 'signup')
                assert r.status_code == 200

                email = f'email-{randhex(16)}@bar.com'
                name = f'name-{randhex(16)}'
                password = randhex(16)

                r = await client.post(
                    base_url + 'signup',
                    content=urllib.parse.urlencode({
                        'email': email,
                        'name': name,
                        'password': password,
                    }),
                )
                assert r.status_code == 302

                r = await client.send(check.not_none(r.next_request))
                assert r.status_code == 200

                ##

                r = await client.post(
                    base_url + 'login',
                    content=urllib.parse.urlencode({
                        'email': email,
                        'password': password,
                    }),
                )
                assert r.status_code == 302

                r = await client.send(check.not_none(r.next_request))
                assert r.status_code == 200

                ##

                auth_token = randhex(16)

                r = await client.post(
                    base_url + 'profile',
                    content=urllib.parse.urlencode({
                        'auth-token': auth_token,
                    }),
                )
                assert r.status_code == 302

                r = await client.send(check.not_none(r.next_request))
                assert r.status_code == 200

            async with httpx.AsyncClient(timeout=get_timeout_s()) as client:
                r = await client.post(
                    base_url + 'check-auth',
                )
                assert r.status_code == 401

                r = await client.post(
                    base_url + 'check-auth',
                    headers={'Authorization': 'Bearer ' + auth_token},
                )
                assert r.status_code == 200

                dct = json.loads(r.read().decode())
                assert dct['user_name'] == name

            if lang.can_import('tiktoken'):
                async with httpx.AsyncClient(timeout=get_timeout_s()) as client:
                    r = await client.post(
                        base_url + 'tik',
                        content='foo bar baz qux hi there',
                        headers={'Authorization': 'Bearer ' + auth_token},
                    )
                    assert r.status_code == 200

                    dct = json.loads(r.read().decode())
                    assert dct['user_name'] == name
                    assert dct['tokens'] == [21943, 2318, 275, 1031, 627, 87, 23105, 612]

    async with inj.create_async_managed_injector(
        bind_app(),
        bind_dbs(),
        bind_secrets(),
        bind_in_memory_user_store(),
    ) as i:
        app = await au.s_to_a(i.provide)(asgi.AsgiApp)

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
