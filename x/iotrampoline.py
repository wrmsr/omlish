"""
TODO:
 - greenlets
 - this prob goes in concurrent?
"""
import collections
import dataclasses as dc
import gzip
import os.path
import threading
import typing as ta

import _compression


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

            lock: threading.RLock | None = None,
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

    def append(self, *items: T, n: int = 1) -> None:
        with self.cond:
            self.deque.extend(items)
            self.cond.notify(n)

    def popleft(self, timeout: float | None = None) -> T:
        with self.cond:
            while not self.deque:
                self.cond.wait(timeout)
            return self.deque.popleft()


class ThreadedIoTrampoline:
    def __init__(self) -> None:
        super().__init__()

        self._in: ConditionDeque[bytes] = ConditionDeque()
        self._out: ConditionDeque[bytes] = ConditionDeque()

        self._thread = threading.Thread(target=self._thread_proc)

    def __enter__(self) -> ta.Self:
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    #

    @dc.dataclass(frozen=True)
    class _ReadFile:
        o: 'ThreadedIoTrampoline'

        def read(self, n: int, /) -> bytes:
            return self.o._out.popleft()

        def seekable(self) -> bool:
            return False

        def seek(self, n: int, /) -> ta.Any:
            raise TypeError

        def close(self) -> None:
            raise NotImplementedError

    def _thread_proc(self) -> None:
        with gzip.GzipFile(fileobj=self._ReadFile(self), mode='rb') as f:
            while out := f.read(0x1000):
                raise NotImplementedError

    def feed(self, *data: bytes) -> ta.Iterable[bytes]:
        raise NotImplementedError


def _main() -> None:
    in_file = os.path.expanduser('~/Downloads/access.json.gz')
    with open(in_file, 'rb') as f:
        with ThreadedIoTrampoline() as iot:
            while raw := f.read(0x1000):
                for out in iot.feed(raw):
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
