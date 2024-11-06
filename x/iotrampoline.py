"""
TODO:
 - greenlets
 - this prob goes in concurrent?
"""
import collections
import contextlib
import dataclasses as dc
import gzip
import io  # noqa
import os.path
import threading
import typing as ta

import _compression  # noqa

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


class ThreadedIoTrampoline:
    def __init__(self) -> None:
        super().__init__()

        self._in: ConditionDeque[bytes | BaseException] = ConditionDeque()
        self._out: ConditionDeque[
            bytes |
            type[NeedMore] |
            type[ThreadedIoTrampoline.Exited] |
            BaseException
        ] = ConditionDeque()

        self._thread = threading.Thread(target=self._thread_proc, daemon=True)
        self._eof = False
        self._closed = False

    class Shutdown(BaseException):  # noqa
        pass

    class Exited(lang.Marker):
        pass

    def __enter__(self) -> ta.Self:
        self._thread.start()
        return self

    def close(self, timeout: float | None = None) -> None:
        if not self._thread.is_alive():
            return
        self._out.push(self.Shutdown())
        self._thread.join(timeout)
        if self._thread.is_alive():
            if timeout is not None:
                raise TimeoutError
            else:
                raise RuntimeError('Failed to join thread')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #

    @dc.dataclass(frozen=True)
    class _ReadFile:
        o: 'ThreadedIoTrampoline'

        # _compression._ReadableFileobj

        def read(self, n: int, /) -> bytes:
            if self.o._closed:
                raise RuntimeError('Closed')
            if self.o._eof:
                return b''
            d = self.o._in.pop(if_empty=lambda: self.o._out.push(NeedMore))
            if isinstance(d, BaseException):
                raise d
            if not d:
                self.o._eof = True
            return d

        def seekable(self) -> bool:
            return False

        def seek(self, n: int, /) -> ta.Any:
            raise TypeError

        def close(self) -> None:
            self.o._closed = True

        # ta._RawIOBase

        def readall(self, *args, **kwargs):
            raise TypeError

        def readinto(self, b: BytesLike) -> int | None:
            o = self.read(len(b))
            if not o:
                return None
            b[:len(o)] = o
            return len(o)

        def readable(self) -> bool:
            return not (self.o._eof or self.o._closed)

        def flush(self) -> None:
            pass

        @property
        def closed(self) -> bool:
            return self.o._closed

    def _thread_proc(self) -> None:
        try:
            with contextlib.closing(BufferedReader(self._ReadFile(self))) as bf:
                with gzip.GzipFile(fileobj=bf, mode='rb') as gf:
                    while out := gf.read(0x1000):
                        self._out.push(out)
                    self._out.push(out)
        except BaseException as e:
            self._out.push(e)
            raise
        finally:
            self._out.push(ThreadedIoTrampoline.Exited)

    def feed(self, *data: bytes) -> ta.Iterable[bytes]:
        self._in.push(*data)
        while e := self._out.pop():
            if isinstance(e, NeedMore):
                break
            elif isinstance(e, BaseException):
                raise e
            elif e is ThreadedIoTrampoline.Exited:
                raise RuntimeError('IO thread exited')
            else:
                yield e


def _main() -> None:
    in_file = os.path.expanduser('~/Downloads/access.json.gz')
    with open(in_file, 'rb') as f:
        with ThreadedIoTrampoline() as iot:
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
