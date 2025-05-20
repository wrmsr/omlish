import dataclasses as dc

from omlish.http import all as hu
from omlish.http import asgi
from omlish.secrets.pwhash import check_password_hash
from omserv.apps.base import url_for
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles
from omserv.apps.sessions import with_session
from omserv.apps.templates import JinjaTemplates

from ...users import UserStore
from ..apps.flashing import flash
from ..apps.login import login_user
from ..apps.users import with_user


##


@dc.dataclass(frozen=True)
class LoginHandler(RouteHandlerHolder):
    _templates: JinjaTemplates
    _users: UserStore

    @handles(Route.get('/login'))
    @with_session
    @with_user
    async def handle_get_login(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        html = self._templates.render('login.html.j2')
        await asgi.start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await asgi.finish_response(send, html)

    @handles(Route.post('/login'))
    @with_session
    @with_user
    async def handle_post_login(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        dct = await asgi.read_form_body(recv)

        email = dct[b'email'].decode()
        password = dct[b'password'].decode()  # noqa
        remember = b'remember' in dct  # noqa

        user = await self._users.get(email=email)  # noqa

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')

            await asgi.redirect_response(send, url_for('login'))
            return

        login_user(user, remember=remember)
        await asgi.redirect_response(send, url_for('profile'))
