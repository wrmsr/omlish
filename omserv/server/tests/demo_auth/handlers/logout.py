from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import redirect_response

from ..base import SESSION
from ..base import Handler_
from ..base import Route
from ..base import handles
from ..base import login_required
from ..base import url_for
from ..base import with_session
from ..base import with_user


class LogoutHandler(Handler_):
    @handles(Route('GET', '/logout'))
    @with_session
    @with_user
    @login_required
    async def handle_get_logout(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        SESSION.get().pop('_user_id', None)
        await redirect_response(send, url_for(''))
