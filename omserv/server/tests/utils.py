import socket
import typing as ta

import anyio
import pytest

from .. import headers


T = ta.TypeVar('T')


TIMEOUT_S: int = 5


def get_free_port(address: str = '') -> int:
    """Find a free TCP port (entirely at random)"""

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((address, 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_exception_chain(ex: BaseException) -> list[BaseException]:
    cur: BaseException | None = ex
    ret: list[BaseException] = []
    while cur is not None:
        ret.append(cur)
        cur = cur.__cause__
    return ret


CONNECTION_REFUSED_EXCEPTION_TYPES: tuple[type[Exception], ...] = (OSError, ConnectionRefusedError)


def is_connection_refused_exception(e: Exception) -> bool:
    return any(isinstance(ce, ConnectionRefusedError) for ce in get_exception_chain(e))


async def anyio_eof_to_empty(fn: ta.Callable[..., ta.Awaitable[T]], *args: ta.Any, **kwargs: ta.Any) -> T | bytes:
    try:
        return await fn(*args, **kwargs)
    except anyio.EndOfStream:
        return b''


@pytest.fixture(autouse=True)
def headers_time_patch(monkeypatch) -> None:
    monkeypatch.setattr(headers, '_now', lambda: 5000)
