import dataclasses as dc

from omlish.http import all as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import finish_response
from omlish.http.asgi import read_form_body
from omlish.http.asgi import redirect_response
from omlish.http.asgi import start_response
from omlish.secrets.pwhash import check_password_hash
from omserv.apps.base import url_for
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandler_
from omserv.apps.routes import handles
from omserv.apps.sessions import with_session
from omserv.apps.templates import JinjaTemplates

from ...users import UserStore
from ..apps.flashing import flash
from ..apps.login import login_user
from ..apps.users import with_user


@dc.dataclass(frozen=True)
class LoginHandler(RouteHandler_):
    _templates: JinjaTemplates
    _users: UserStore

    @handles(Route.get('/login'))
    @with_session
    @with_user
    async def handle_get_login(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        html = self._templates.render('login.html.j2')
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)

    @handles(Route.post('/login'))
    @with_session
    @with_user
    async def handle_post_login(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        dct = await read_form_body(recv)

        email = dct[b'email'].decode()
        password = dct[b'password'].decode()  # noqa
        remember = b'remember' in dct  # noqa

        user = await self._users.get(email=email)  # noqa

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')

            await redirect_response(send, url_for('login'))
            return

        login_user(user, remember=remember)
        await redirect_response(send, url_for('profile'))
