# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import contextlib
import socket
import typing as ta

from ..lite.check import check
from ..lite.timeouts import Timeout
from ..lite.timeouts import TimeoutLike


##


DEFAULT_AVAILABLE_PORT_HOST: str = '127.0.0.1'


@contextlib.contextmanager
def get_available_port_context(
        host: ta.Optional[str] = None,
        family: int = socket.AF_INET,
        type: int = socket.SOCK_STREAM,  # noqa
        *,
        listen: ta.Union[bool, int, None] = False,
) -> ta.Iterator[int]:
    if host is None:
        host = DEFAULT_AVAILABLE_PORT_HOST

    if listen is not None:
        if listen is True:
            listen = 1
        elif listen is False:
            listen = None
        else:
            listen = check.isinstance(listen, int)

    with socket.socket(family, type) as sock:
        sock.bind((host, 0))

        if listen is not None:
            sock.listen(listen)

        port = sock.getsockname()[1]

        yield port


def get_available_port(*args: ta.Any, **kwargs: ta.Any) -> int:
    with get_available_port_context(*args, **kwargs) as port:
        return port


def get_available_ports(
        n: int,
        *,
        host: ta.Optional[str] = None,
        exclude: ta.Optional[ta.Iterable[int]] = None,
        timeout: TimeoutLike = None,
) -> ta.List[int]:
    exclude = set(exclude or [])

    seen: ta.Set[int] = set()
    ret: ta.List[int] = []

    timeout = Timeout.of(timeout)

    with contextlib.ExitStack() as es:
        while len(ret) < n:
            timeout()

            cur = es.enter_context(get_available_port_context(host))

            check.not_in(cur, seen)
            seen.add(cur)

            if cur not in exclude:
                ret.append(cur)

    return ret
