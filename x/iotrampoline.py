"""
TODO:
 - greenlets
"""
import gzip
import os.path
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
    in_file = os.path.expanduser('~/Downloads/access.json.gz')

    class ThreadFile:
        def read(self, n: int, /) -> bytes:
            raise NotImplementedError

        def seekable(self) -> bool:
            return False

        def seek(self, n: int, /) -> ta.Any:
            raise TypeError

        def close(self) -> None:
            raise NotImplementedError

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
