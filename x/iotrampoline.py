"""
TODO:
 - greenlets
"""
import collections
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


def _main() -> None:
    class ThreadFile:
        def __init__(self) -> None:
            super().__init__()
            self._cond = threading.Condition()
            self._queue: collections.deque = collections.deque()

        def enqueue(self, buf: bytes) -> None:
            with self._cond:
                self._queue.append(buf)
                self._cond.notify()

        def read(self, n: int, /) -> bytes:
            with self._cond:
                while not self._queue:
                    self._cond.wait()
                return self._queue.popleft()

        def seekable(self) -> bool:
            return False

        def seek(self, n: int, /) -> ta.Any:
            raise TypeError

        def close(self) -> None:
            raise NotImplementedError

    tf = ThreadFile()

    def thread_proc() -> None:
        pass

    thr = threading.Thread(target=thread_proc)
    thr.start()

    ##

    in_file = os.path.expanduser('~/Downloads/access.json.gz')

    with gzip.GzipFile(fileobj=ThreadFile(), mode='rb') as f:
        while data := f.read(0x1000):
            print(data)

    # ibc = nop_incremental_bytes_codec
    # with open(in_file, 'rb') as f:
    #     while data := f.read(0x1000):
    #         print(ibc(data))
    # print(ibc(None))


if __name__ == '__main__':
    _main()
