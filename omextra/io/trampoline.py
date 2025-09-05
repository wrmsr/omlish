import abc
import contextlib
import io
import typing as ta

from omlish import check
from omlish import lang
from omlish.concurrent import threadlets as tls
from omlish.sync import ConditionDeque


if ta.TYPE_CHECKING:
    import threading

    from omlish.io import pyio  # noqa

else:
    threading = lang.proxy_import('threading')

    pyio = lang.proxy_import('omlish.io.pyio')


T = ta.TypeVar('T')

BytesLike: ta.TypeAlias = ta.Any

BufferedReader: ta.TypeAlias = io.BufferedReader
# BufferedReader: ta.TypeAlias = pyio.BufferedReader


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
    def feed(self, *data: bytes) -> ta.Iterator[bytes]:
        raise NotImplementedError


#


class ThreadIoTrampoline(IoTrampoline):
    def __init__(self, target: IoTrampolineTarget, **kwargs: ta.Any) -> None:
        super().__init__(target, **kwargs)

        self._in: ConditionDeque[bytes | BaseException] = ConditionDeque()
        self._out: ConditionDeque[
            bytes |  # noqa
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

    def _read(self, n: int, /) -> bytes | BaseException:
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

    def feed(self, *data: bytes) -> ta.Iterator[bytes]:
        self._in.push(*data)
        while True:
            e = self._out.pop()
            if e is NeedMore:
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


#


class ThreadletIoTrampoline(IoTrampoline):
    def __init__(
            self,
            target: IoTrampolineTarget,
            threadlets: tls.Threadlets = tls.GREENLET_THREADLETS,
            ** kwargs: ta.Any,
    ) -> None:
        super().__init__(target, **kwargs)

        self._proxy = ProxyReadFile(self._read)
        self._tl: tls.Threadlet = threadlets.spawn(self._g_proc)

    #

    def close(self, timeout: float | None = None) -> None:
        if self._tl.dead:
            return
        out = self._tl.switch(Shutdown())
        if out is not Exited or not self._tl.dead:
            raise RuntimeError

    #

    def __enter__(self) -> ta.Self:
        out = self._tl.switch()
        if out is not NeedMore:
            raise RuntimeError
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #

    def _read(self, n: int, /) -> bytes:
        out = check.not_none(self._tl.parent).switch(NeedMore)
        return out

    def _g_proc(self) -> ta.Any:
        try:
            with contextlib.closing(self._make_buffered_reader(self._proxy)) as bf:  # noqa
                with self._target(bf) as read:
                    while out := read():
                        e = check.not_none(self._tl.parent).switch(out)
                        if e is not NeedMore:
                            raise TypeError(e)  # noqa
                    e = check.not_none(self._tl.parent).switch(out)
                    if not isinstance(e, Shutdown):
                        raise TypeError(e)  # noqa
            return Exited
        except BaseException as e:
            check.not_none(self._tl.parent).throw(e)
            raise

    def feed(self, *data: bytes) -> ta.Iterator[bytes]:
        i: bytes | type[NeedMore]
        for i in data:
            while True:
                e = self._tl.switch(i)
                i = NeedMore
                if e is NeedMore:
                    break
                elif isinstance(e, bytes):
                    yield e
                    if not e:
                        return
                else:
                    raise TypeError(e)
