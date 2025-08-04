from omlish.http import asgi

from .....apps.base import url_for
from .....apps.routes import Route
from .....apps.routes import RouteHandlerHolder
from .....apps.routes import handles
from .....apps.sessions import SESSION
from .....apps.sessions import with_session
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
