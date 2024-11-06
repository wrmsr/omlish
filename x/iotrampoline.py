"""
TODO:
 - greenlets
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


class ThreadedIoTrampoline:
    def __init__(self) -> None:
        super().__init__()

        self._in_cond = threading.Condition()
        self._in_queue: collections.deque = collections.deque()

        self._out_cond = threading.Condition()
        self._out_queue: collections.deque = collections.deque()

        self._thread = threading.Thread(target=self._thread_proc)

    def __enter__(self) -> ta.Self:
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def enqueue_input(self, buf: bytes) -> None:
        with self._in_cond:
            self._in_queue.append(buf)
            self._in_cond.notify()

    def _await_input(self, n: int) -> bytes:
        with self._in_cond:
            while not self._in_queue:
                self._in_cond.wait()
            return self._in_queue.popleft()

    @dc.dataclass(frozen=True)
    class _ReadFile:
        o: 'ThreadedIoTrampoline'

        def read(self, n: int, /) -> bytes:
            return self.o._await_input(n)

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


def _main() -> None:
    in_file = os.path.expanduser('~/Downloads/access.json.gz')
    with open(in_file, 'rb') as f:
        with ThreadedIoTrampoline() as iot:
            while raw := f.read(0x1000):
                iot.enqueue_input(raw)
                out = b''
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
