import dataclasses as dc
import typing as ta

from omlish import check
from omlish import http as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import finish_response
from omlish.http.asgi import read_form_body
from omlish.http.asgi import redirect_response
from omlish.http.asgi import start_response

from ...users import User
from ...users import UserStore
from ..apps.base import url_for
from ..apps.j2 import J2Templates
from ..apps.login import login_required
from ..apps.routes import Handler_
from ..apps.routes import Route
from ..apps.routes import handles
from ..apps.sessions import with_session
from ..apps.users import with_user


@dc.dataclass(frozen=True)
class ProfileHandler(Handler_):
    _current_user: ta.Callable[[], User | None]
    _templates: J2Templates
    _users: UserStore

    @handles(Route('GET', '/profile'))
    @with_session
    @with_user
    @login_required
    async def handle_get_profile(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        user = check.not_none(self._current_user())
        html = self._templates.render(
            'profile.html.j2',
            name=user.name,
            auth_token=user.auth_token or '',
        )
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)

    @handles(Route('POST', '/profile'))
    @with_session
    @with_user
    async def handle_post_profile(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        user = check.not_none(self._current_user())

        dct = await read_form_body(recv)

        auth_token = dct[b'auth-token'].decode()

        user = dc.replace(user, auth_token=auth_token or None)
        self._users.update(user)

        await redirect_response(send, url_for('profile'))
