from omlish.http import asgi
from omserv.apps.base import url_for
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles
from omserv.apps.sessions import SESSION
from omserv.apps.sessions import with_session

from ..apps.login import login_required
from ..apps.users import with_user


class LogoutHandler(RouteHandlerHolder):
    @handles(Route.get('/logout'))
    @with_session
    @with_user
    @login_required
    async def handle_get_logout(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        SESSION.get().pop('_user_id', None)
        await asgi.redirect_response(send, url_for(''))
