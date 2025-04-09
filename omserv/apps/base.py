import contextvars
import typing as ta

from omlish.http import asgi


##


SCOPE: contextvars.ContextVar[asgi.Scope] = contextvars.ContextVar('scope')


##


BaseServerUrl = ta.NewType('BaseServerUrl', str)


BASE_SERVER_URL: contextvars.ContextVar[BaseServerUrl] = contextvars.ContextVar('base_server_url')


def url_for(s: str) -> str:
    return BASE_SERVER_URL.get() + s
