"""
TODO:
 - greenlets
 - this prob goes in concurrent?
"""
import abc
import collections
import contextlib
import dataclasses as dc
import gzip
import io  # noqa
import os.path
import threading
import typing as ta

import _compression  # noqa

import greenlet

from omlish import lang

from . import pyio  # noqa


"""
class _Reader(Protocol):
    def read(self, n: int, /) -> bytes: ...
    def seekable(self) -> bool: ...
    def seek(self, n: int, /) -> Any: ...

class _ReadableFileobj(_Reader, Protocol): ...
    # The following attributes and methods are optional:
    # def fileno(self) -> int: ...
    # def close(self) -> object: ...

class _WritableFileobj(Protocol):
    def write(self, b: bytes, /) -> object: ...
    # The following attributes and methods are optional:
    # def fileno(self) -> int: ...
    # def close(self) -> object: ...
"""


# Unlike regular files, empty bytes does not mean eof - None does.
IncrementalBytesCodec: ta.TypeAlias = ta.Callable[[bytes], bytes | None]


def nop_incremental_bytes_codec(data: bytes | None) -> bytes | None:
    return data


T = ta.TypeVar('T')


class ConditionDeque(ta.Generic[T]):
    def __init__(
            self,
            *,
            cond: threading.Condition | None = None,
            deque: collections.deque[T] | None = None,

            lock: ta.Optional['threading.RLock'] = None,
            maxlen: int | None = None,
            init: ta.Iterable[T] | None = None,
    ) -> None:
        super().__init__()

        if cond is None:
            cond = threading.Condition(lock=lock)
        if deque is None:
            deque = collections.deque(maxlen=maxlen)
        if init:
            deque.extend(init)

        self._cond = cond
        self._deque = deque

    @property
    def cond(self) -> threading.Condition:
        return self._cond

    @property
    def deque(self) -> collections.deque[T]:
        return self._deque

    def push(
            self,
            *items: T,
            n: int = 1,
    ) -> None:
        with self.cond:
            self.deque.extend(items)
            self.cond.notify(n)

    def pop(
            self,
            timeout: float | None = None,
            *,
            if_empty: ta.Callable[[], None] | None = None,
    ) -> T:
        with self.cond:
            if not self.deque and if_empty is not None:
                if_empty()
            while not self.deque:
                self.cond.wait(timeout)
            return self.deque.popleft()


class NeedMore(lang.Marker):
    pass


BytesLike: ta.TypeAlias = ta.Any


BufferedReader = io.BufferedReader
# BufferedReader = pyio.BufferedReader


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


class Exited(lang.Marker):
    pass


class Shutdown(BaseException):  # noqa
    pass


class IoTrampoline(lang.Abstract):
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


class ThreadedIoTrampoline(IoTrampoline):
    def __init__(self) -> None:
        super().__init__()

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
            with contextlib.closing(BufferedReader(self._proxy)) as bf:  # noqa
                with gzip.GzipFile(fileobj=bf, mode='rb') as gf:
                    while out := gf.read(0x1000):
                        self._out.push(out)
                    self._out.push(out)
        except BaseException as e:
            self._out.push(e)
            raise
        finally:
            self._out.push(Exited)

    def feed(self, *data: bytes) -> ta.Iterable[bytes]:
        self._in.push(*data)
        while e := self._out.pop():
            if isinstance(e, NeedMore):
                break
            elif isinstance(e, BaseException):
                raise e
            elif e is Exited:
                raise RuntimeError('IO thread exited')
            else:
                yield e


class GreenletIoTrampoline(IoTrampoline):
    def __init__(self) -> None:
        super().__init__()

        self._proxy = ProxyReadFile(self._read)
        self._g = greenlet.greenlet(self._g_proc)

    #

    def close(self, timeout: float | None = None) -> None:
        if self._g.dead:
            return
        out = self._g.switch(Shutdown())
        raise NotImplementedError

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
        return self._g.parent.switch(NeedMore)

    def _g_proc(self) -> None:
        try:
            with contextlib.closing(BufferedReader(self._proxy)) as bf:  # noqa
                with gzip.GzipFile(fileobj=bf, mode='rb') as gf:
                    while out := gf.read(0x1000):
                        self._g.parent.switch(out)
                    self._g.parent.switch(out)
        except BaseException as e:
            self._g.parent.switch(e)
            raise
        finally:
            self._g.parent.switch(Exited)

    def feed(self, *data: bytes) -> ta.Iterable[bytes]:
        for buf in data:
            out = self._g.switch(buf)
            if out is NeedMore:
                break
            elif isinstance(out, bytes):
                yield out
            else:
                raise TypeError(out)


def _main() -> None:
    in_file = os.path.expanduser('~/Downloads/access.json.gz')
    with open(in_file, 'rb') as f:
        with GreenletIoTrampoline() as iot:
            while raw := f.read(0x1000):
                for out in iot.feed(raw):
                    print(out)
            for out in iot.feed(b''):
                print(out)

    ##

    # with gzip.GzipFile(fileobj=ThreadFile(), mode='rb') as f:
    #     while data := f.read(0x1000):
    #         print(data)

    # ibc = nop_incremental_bytes_codec
    # with open(in_file, 'rb') as f:
    #     while data := f.read(0x1000):
    #         print(ibc(data))
    # print(ibc(None))


if __name__ == '__main__':
    _main()
