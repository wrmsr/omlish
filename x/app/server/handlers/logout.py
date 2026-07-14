from omcore.http import asgi
from omcore.http.apps.base import url_for
from omcore.http.apps.routes import Route
from omcore.http.apps.routes import RouteHandlerHolder
from omcore.http.apps.routes import handles
from omcore.http.apps.sessions import SESSION
from omcore.http.apps.sessions import with_session

from ..apps.login import login_required
from ..apps.users import with_user


##


class LogoutHandler(RouteHandlerHolder):
    @handles(Route.get('/logout'))
    @with_session
    @with_user
    @login_required
    async def handle_get_logout(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        SESSION.get().pop('_user_id', None)
        await asgi.redirect_response(send, url_for(''))
