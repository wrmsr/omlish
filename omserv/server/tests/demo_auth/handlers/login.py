import typing as ta

from omlish import http as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import finish_response
from omlish.http.asgi import read_form_body
from omlish.http.asgi import redirect_response
from omlish.http.asgi import start_response

from ..base import Handler_
from ..base import Route
from ..base import RouteHandler
from ..base import flash
from ..base import login_user
from ..base import url_for
from ..base import with_session
from ..base import with_user
from ..j2 import J2Templates
from ..passwords import check_password_hash
from ..users import UserStore


class LoginHandler(Handler_):
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
            RouteHandler(Route('GET', '/login'), self.handle_get_login),  # noqa
            RouteHandler(Route('POST', '/login'), self.handle_post_login),  # noqa
        ]

    @with_session
    @with_user
    async def handle_get_login(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        html = self._templates.render('login.html.j2')
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)

    @with_session
    @with_user
    async def handle_post_login(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        dct = await read_form_body(recv)

        email = dct[b'email'].decode()
        password = dct[b'password'].decode()  # noqa
        remember = b'remember' in dct  # noqa

        user = self._users.get(email=email)  # noqa

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')

            await redirect_response(send, url_for('login'))
            return

        login_user(user, remember=remember)
        await redirect_response(send, url_for('profile'))
