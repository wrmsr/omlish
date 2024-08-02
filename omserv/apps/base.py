import contextvars

from omlish.http.asgi import AsgiScope


SCOPE: contextvars.ContextVar[AsgiScope] = contextvars.ContextVar('scope')
