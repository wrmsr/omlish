from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import redirect_response
from omserv.apps.routes import Handler_
from omserv.apps.routes import Route
from omserv.apps.routes import handles
from omserv.apps.sessions import SESSION
from omserv.apps.sessions import with_session

from ..apps.base import url_for
from ..apps.login import login_required
from ..apps.users import with_user


class LogoutHandler(Handler_):
    @handles(Route.get('/logout'))
    @with_session
    @with_user
    @login_required
    async def handle_get_logout(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        SESSION.get().pop('_user_id', None)
        await redirect_response(send, url_for(''))
