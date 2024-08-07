"""
TODO:
 - remember - just a second cookie lol
 - chrome save text boxes / login
 - with_session / with_user / login_required as *marks* not wrappers
  - maybe *both*, just to last-ditch validate login_required
 - logout is POST

https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import contextlib
import logging
import typing as ta

from omlish import asyncs as au
from omlish import inject as inj
from omlish import lang
from omlish.http.asgi import AsgiApp

from .inject import bind


log = logging.getLogger(__name__)


@lang.cached_function
def _server_app() -> AsgiApp:
    return inj.create_injector(bind()).provide(AsgiApp)


@contextlib.asynccontextmanager
async def server_app_context() -> ta.AsyncIterator[AsgiApp]:
    async with inj.create_async_managed_injector(
        bind(),
    ) as i:
        app = await au.s_to_a(i.provide)(AsgiApp)
        yield app
