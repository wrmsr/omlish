import dataclasses as dc

from omlish import http as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import finish_response
from omlish.http.asgi import read_form_body
from omlish.http.asgi import redirect_response
from omlish.http.asgi import start_response
from omserv.passwords import generate_password_hash

from ..base import Handler_
from ..base import Route
from ..base import handles
from ..base import url_for
from ..base import with_session
from ..base import with_user
from ..j2 import J2Templates
from ..users import UserStore


@dc.dataclass(frozen=True)
class SignupHandler(Handler_):
    _templates: J2Templates
    _users: UserStore

    @handles(Route('GET', '/signup'))
    @with_session
    @with_user
    async def handle_get_signup(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        html = self._templates.render('signup.html.j2')
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)

    @handles(Route('POST', '/signup'))
    @with_session
    @with_user
    async def handle_post_signup(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        dct = await read_form_body(recv)

        email = dct[b'email'].decode()
        password = dct[b'password'].decode()
        name = dct[b'name'].decode()

        self._users.create(
            email=email,
            password=generate_password_hash(password, method='scrypt'),
            name=name,
        )

        await redirect_response(send, url_for('login'))
