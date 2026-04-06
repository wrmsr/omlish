import typing as ta

from ... import lang
from .core import AsyncConn
from .core import AsyncDb
from .core import Conn
from .core import Db


##


def sync_connect(obj: Conn | Db) -> ta.ContextManager[Conn]:
    if isinstance(obj, Conn):
        return lang.ValueContextManager(obj)
    elif isinstance(obj, Db):
        return obj.connect()
    else:
        raise TypeError(obj)


def async_connect(obj: AsyncConn | AsyncDb) -> ta.AsyncContextManager[AsyncConn]:
    if isinstance(obj, AsyncConn):
        return lang.ValueAsyncContextManager(obj)
    elif isinstance(obj, AsyncDb):
        return obj.connect()
    else:
        raise TypeError(obj)


@ta.overload
def connect(obj: Conn | Db) -> ta.ContextManager[Conn]:
    ...


@ta.overload
def connect(obj: AsyncConn | AsyncDb) -> ta.AsyncContextManager[AsyncConn]:
    ...


def connect(obj):
    if isinstance(obj, (Conn, Db)):
        return sync_connect(obj)
    elif isinstance(obj, (AsyncConn, AsyncDb)):
        return async_connect(obj)
    else:
        raise TypeError(obj)
