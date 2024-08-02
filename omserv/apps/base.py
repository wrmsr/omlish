import contextvars
import os

from omlish.http.asgi import AsgiScope

from .j2 import j2_helper


##


SCOPE: contextvars.ContextVar[AsgiScope] = contextvars.ContextVar('scope')


##


def base_server_url() -> str:
    return os.environ.get('BASE_SERVER_URL', 'http://localhost:8000/')


@j2_helper
def url_for(s: str) -> str:
    return base_server_url() + s
