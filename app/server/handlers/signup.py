import dataclasses as dc

from omlish.http import all as hu
from omlish.http import asgi
from omlish.secrets.pwhash import generate_password_hash
from omserv.apps.base import url_for
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles
from omserv.apps.sessions import with_session
from omserv.apps.templates import JinjaTemplates

from ...users import UserStore
from ..apps.users import with_user


##


@dc.dataclass(frozen=True)
class SignupHandler(RouteHandlerHolder):
    _templates: JinjaTemplates
    _users: UserStore

    @handles(Route.get('/signup'))
    @with_session
    @with_user
    async def handle_get_signup(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        html = self._templates.render('signup.html.j2')
        await asgi.start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await asgi.finish_response(send, html)

    @handles(Route.post('/signup'))
    @with_session
    @with_user
    async def handle_post_signup(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        dct = await asgi.read_form_body(recv)

        email = dct[b'email'].decode()
        password = dct[b'password'].decode()
        name = dct[b'name'].decode()

        await self._users.create(
            email=email,
            password=generate_password_hash(password, method='scrypt'),
            name=name,
        )

        await asgi.redirect_response(send, url_for('login'))
