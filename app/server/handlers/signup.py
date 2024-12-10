import dataclasses as dc

from omlish.http import all as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import finish_response
from omlish.http.asgi import read_form_body
from omlish.http.asgi import redirect_response
from omlish.http.asgi import start_response
from omlish.secrets.pwhash import generate_password_hash
from omserv.apps.base import url_for
from omserv.apps.routes import Handler_
from omserv.apps.routes import Route
from omserv.apps.routes import handles
from omserv.apps.sessions import with_session
from omserv.apps.templates import JinjaTemplates

from ...users import UserStore
from ..apps.users import with_user


@dc.dataclass(frozen=True)
class SignupHandler(Handler_):
    _templates: JinjaTemplates
    _users: UserStore

    @handles(Route.get('/signup'))
    @with_session
    @with_user
    async def handle_get_signup(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        html = self._templates.render('signup.html.j2')
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)

    @handles(Route.post('/signup'))
    @with_session
    @with_user
    async def handle_post_signup(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        dct = await read_form_body(recv)

        email = dct[b'email'].decode()
        password = dct[b'password'].decode()
        name = dct[b'name'].decode()

        await self._users.create(
            email=email,
            password=generate_password_hash(password, method='scrypt'),
            name=name,
        )

        await redirect_response(send, url_for('login'))
