# ruff: noqa: UP006 UP007
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
def get_available_port_context(host: ta.Optional[str] = None) -> ta.Iterator[int]:
    if host is None:
        host = DEFAULT_AVAILABLE_PORT_HOST

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        sock.listen(1)
        port = sock.getsockname()[1]
        yield port


def get_available_port(host: ta.Optional[str] = None) -> int:
    with get_available_port_context(host) as port:
        pass
    return port


def get_available_ports(
        n: int,
        *,
        host: ta.Optional[str] = None,
        exclude: ta.Optional[ta.Iterable[int]] = None,
        timeout: ta.Optional[TimeoutLike] = None,
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
