# ruff: noqa: UP006 UP007
import typing as ta

from .proxy import AsyncIoProxy


AnyStrT = ta.TypeVar('AnyStrT', bytes, str)


##


class TypingIOAsyncIoProxy(AsyncIoProxy, ta.Generic[AnyStrT], proxied_cls=ta.IO):
    @property
    def mode(self) -> str:
        raise TypeError

    @property
    def name(self) -> str:
        raise TypeError

    async def close(self) -> None:
        raise TypeError

    @property
    def closed(self) -> bool:
        raise TypeError

    def fileno(self) -> int:
        raise TypeError

    async def flush(self) -> None:
        raise TypeError

    def isatty(self) -> bool:
        raise TypeError

    async def read(self, n: int = -1) -> AnyStrT:
        raise TypeError

    def readable(self) -> bool:
        raise TypeError

    async def readline(self, limit: int = -1) -> AnyStrT:
        raise TypeError

    async def readlines(self, hint: int = -1) -> ta.List[AnyStrT]:
        raise TypeError

    async def seek(self, offset: int, whence: int = 0) -> int:
        raise TypeError

    def seekable(self) -> bool:
        raise TypeError

    async def tell(self) -> int:
        raise TypeError

    async def truncate(self, size: int = None) -> int:
        raise TypeError

    def writable(self) -> bool:
        raise TypeError

    async def write(self, s: AnyStrT) -> int:
        raise TypeError

    async def writelines(self, lines: ta.List[AnyStrT]) -> None:
        raise TypeError

    # def __enter__(self) -> 'IO[AnyStrT]':
    #     pass

    # def __exit__(self, type, value, traceback) -> None:
    #     pass


class TypingBinaryIOAsyncIoProxy(TypingIOAsyncIoProxy[bytes], proxied_cls=ta.BinaryIO):
    def write(self, s: ta.Union[bytes, bytearray]) -> int:
        raise TypeError

    # def __enter__(self) -> 'BinaryIO':
    #     pass


class TypingTextIOAsyncIoProxy(TypingIOAsyncIoProxy[str], proxied_cls=ta.TextIO):
    # @property
    # def buffer(self) -> BinaryIO:
    #     pass

    @property
    def encoding(self) -> str:
        raise TypeError

    @property
    def errors(self) -> ta.Optional[str]:
        raise TypeError

    @property
    def line_buffering(self) -> bool:
        raise TypeError

    @property
    def newlines(self) -> ta.Any:
        raise TypeError

    # def __enter__(self) -> 'TextIO':
    #     pass
