"""
TODO:
 - concurrent.Threadlets
 - https://docs.python.org/3/library/zlib.html#zlib.compressobj
"""
import abc
import contextlib
import gzip
import io
import typing as ta

import greenlet

from .. import lang
from ..sync import ConditionDeque


if ta.TYPE_CHECKING:
    import threading

    from . import pyio  # noqa
else:
    threading = lang.proxy_import('threading')

    pyio = lang.proxy_import('.pyio', __package__)


T = ta.TypeVar('T')

BytesLike: ta.TypeAlias = ta.Any

BufferedReader = io.BufferedReader
# BufferedReader = pyio.BufferedReader


##


class ProxyReadFile:
    def __init__(self, read: ta.Callable[[int], bytes | BaseException]) -> None:
        super().__init__()

        self._read = read
        self._eof = False
        self._closed = False

    #

    def read(self, n: int, /) -> bytes:
        if self._closed:
            raise RuntimeError('Closed')
        if self._eof:
            return b''
        d = self._read(n)
        if isinstance(d, BaseException):
            raise d
        if not d:
            self._eof = True
        return d

    def readall(self, *args, **kwargs):
        raise TypeError  # FIXME

    def readinto(self, b: BytesLike) -> int | None:
        d = self.read(len(b))
        if d:
            b[:len(d)] = d
        return len(d)

    #

    def readable(self) -> bool:
        return not (self._eof or self._closed)

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        self._closed = True

    #

    def flush(self) -> None:
        pass

    def seekable(self) -> bool:
        return False

    def seek(self, n: int, /) -> ta.Any:
        raise TypeError


##


class NeedMore(lang.Marker):
    pass


class Exited(lang.Marker):
    pass


class Shutdown(BaseException):  # noqa
    pass


IoTrampolineTarget: ta.TypeAlias = ta.Callable[[io.BufferedReader], ta.ContextManager[ta.Callable[[], bytes]]]


class IoTrampoline(lang.Abstract):
    def __init__(
            self,
            target: IoTrampolineTarget,
            *,
            buffer_size: int | None = None,
    ) -> None:
        super().__init__()

        self._target = target
        self._buffer_size = buffer_size

    def _make_buffered_reader(self, raw: ta.Any) -> io.BufferedReader:
        return io.BufferedReader(
            raw,
            **(dict(buffer_size=self._buffer_size) if self._buffer_size is not None else {}),
        )

    @abc.abstractmethod
    def close(self, timeout: float | None = None) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def __enter__(self) -> ta.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abc.abstractmethod
    def feed(self, *data: bytes) -> ta.Iterable[bytes]:
        raise NotImplementedError


class ThreadIoTrampoline(IoTrampoline):
    def __init__(self, target: IoTrampolineTarget, **kwargs: ta.Any) -> None:
        super().__init__(target, **kwargs)

        self._in: ConditionDeque[bytes | BaseException] = ConditionDeque()
        self._out: ConditionDeque[
            bytes |
            type[NeedMore] |
            type[Exited] |
            BaseException
        ] = ConditionDeque()

        self._proxy = ProxyReadFile(self._read)

        self._thread = threading.Thread(target=self._thread_proc, daemon=True)

    #

    def close(self, timeout: float | None = None) -> None:
        if not self._thread.is_alive():
            return
        self._out.push(Shutdown())
        self._thread.join(timeout)
        if self._thread.is_alive():
            if timeout is not None:
                raise TimeoutError
            else:
                raise RuntimeError('Failed to join thread')

    #

    def __enter__(self) -> ta.Self:
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #

    def _read(self, n: int, /) -> bytes:
        return self._in.pop(if_empty=lambda: self._out.push(NeedMore))

    def _thread_proc(self) -> None:
        try:
            with contextlib.closing(self._make_buffered_reader(self._proxy)) as bf:  # noqa
                with self._target(bf) as read:
                    while out := read():
                        self._out.push(out)
                    self._out.push(out)
        except BaseException as e:
            self._out.push(e)
            raise
        finally:
            self._out.push(Exited)

    def feed(self, *data: bytes) -> ta.Iterable[bytes]:
        self._in.push(*data)
        while True:
            e = self._out.pop()
            if isinstance(e, NeedMore):
                break
            elif isinstance(e, BaseException):
                raise e
            elif e is Exited:
                raise RuntimeError('IO thread exited')
            elif isinstance(e, bytes):
                yield e
                if not e:
                    return
            else:
                raise TypeError(e)


class GreenletIoTrampoline(IoTrampoline):
    def __init__(self, target: IoTrampolineTarget, **kwargs: ta.Any) -> None:
        super().__init__(target, **kwargs)

        self._proxy = ProxyReadFile(self._read)
        self._g = greenlet.greenlet(self._g_proc)

    #

    def close(self, timeout: float | None = None) -> None:
        if self._g.dead:
            return
        out = self._g.switch(Shutdown())
        if out is not Exited or not self._g.dead:
            raise RuntimeError

    #

    def __enter__(self) -> ta.Self:
        out = self._g.switch()
        if out is not NeedMore:
            raise RuntimeError
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #

    def _read(self, n: int, /) -> bytes:
        out = self._g.parent.switch(NeedMore)
        return out

    def _g_proc(self) -> ta.Any:
        try:
            with contextlib.closing(BufferedReader(self._proxy)) as bf:  # noqa
                with self._target(bf) as read:
                    while out := read():
                        e = self._g.parent.switch(out)
                        if e is not NeedMore:
                            raise TypeError(e)
                    e = self._g.parent.switch(out)
                    if not isinstance(e, Shutdown):
                        raise TypeError(e)
            return Exited
        except BaseException as e:
            self._g.parent.throw(e)
            raise

    def feed(self, *data: bytes) -> ta.Iterable[bytes]:
        i: bytes | type[NeedMore]
        for i in data:
            while True:
                e = self._g.switch(i)
                i = NeedMore
                if e is NeedMore:
                    break
                elif isinstance(e, bytes):
                    yield e
                    if not e:
                        return
                else:
                    raise TypeError(e)
