import dataclasses as dc
import typing as ta

from omlish import check
from omlish.http import all as hu
from omlish.http import asgi
from omserv.apps.base import url_for
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles
from omserv.apps.sessions import with_session
from omserv.apps.templates import JinjaTemplates

from ...users import User
from ...users import UserStore
from ..apps.login import login_required
from ..apps.users import with_user


@dc.dataclass(frozen=True)
class ProfileHandler(RouteHandlerHolder):
    _current_user: ta.Callable[[], User | None]
    _templates: JinjaTemplates
    _users: UserStore

    @handles(Route.get('/profile'))
    @with_session
    @with_user
    @login_required
    async def handle_get_profile(self, scope: asgi.AsgiScope, recv: asgi.AsgiRecv, send: asgi.AsgiSend) -> None:
        user = check.not_none(self._current_user())
        html = self._templates.render(
            'profile.html.j2',
            name=user.name,
            auth_token=user.auth_token or '',
        )
        await asgi.start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await asgi.finish_response(send, html)

    @handles(Route.post('/profile'))
    @with_session
    @with_user
    async def handle_post_profile(self, scope: asgi.AsgiScope, recv: asgi.AsgiRecv, send: asgi.AsgiSend) -> None:
        user = check.not_none(self._current_user())

        dct = await asgi.read_form_body(recv)

        auth_token = dct[b'auth-token'].decode()

        user = dc.replace(user, auth_token=auth_token or None)
        await self._users.update(user)

        await asgi.redirect_response(send, url_for('profile'))
