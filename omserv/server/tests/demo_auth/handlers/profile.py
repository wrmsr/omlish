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

from ..base import USER
from ..base import Handler_
from ..base import Route
from ..base import RouteHandler
from ..base import login_required
from ..base import url_for
from ..base import with_session
from ..base import with_user
from ..j2 import J2Templates
from ..users import UserStore


class ProfileHandler(Handler_):
    def __init__(
            self,
            templates: J2Templates,
            users: UserStore,
    ) -> None:
        super().__init__()
        self._templates = templates
        self._users = users

    def get_route_handlers(self) -> ta.Iterable[RouteHandler]:
        return [
            RouteHandler(Route('GET', '/profile'), self.handle_get_profile),  # noqa
            RouteHandler(Route('POST', '/profile'), self.handle_post_profile),  # noqa
        ]

    @with_session
    @with_user
    @login_required
    async def handle_get_profile(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        user = check.not_none(USER.get())
        html = self._templates.render(
            'profile.html.j2',
            name=user.name,
            auth_token=user.auth_token or '',
        )
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)

    @with_session
    @with_user
    async def handle_post_profile(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        user = check.not_none(USER.get())

        dct = await read_form_body(recv)

        auth_token = dct[b'auth-token'].decode()

        user = dc.replace(user, auth_token=auth_token or None)
        self._users.update(user)

        await redirect_response(send, url_for('profile'))
