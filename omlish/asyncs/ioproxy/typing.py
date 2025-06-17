# ruff: noqa: UP006 UP007 UP045
import typing as ta

from .proxy import AsyncIoProxy
from .proxy import _register_async_io_proxy_cls


SelfT = ta.TypeVar('SelfT')

AnyStrT = ta.TypeVar('AnyStrT', bytes, str)


##


@_register_async_io_proxy_cls
class TypingIO_AsyncIoProxy(AsyncIoProxy, ta.Generic[AnyStrT], proxied_cls=ta.IO):  # noqa
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

    async def truncate(self, size: ta.Optional[int] = None) -> int:
        raise TypeError

    def writable(self) -> bool:
        raise TypeError

    async def write(self, s: AnyStrT) -> int:
        raise TypeError

    async def writelines(self, lines: ta.List[AnyStrT]) -> None:
        raise TypeError

    async def __aenter__(self: SelfT) -> SelfT:
        raise TypeError

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        raise TypeError


@_register_async_io_proxy_cls
class TypingBinaryIO_AsyncIoProxy(TypingIO_AsyncIoProxy[bytes], proxied_cls=ta.BinaryIO):  # noqa
    def write(self, s: ta.Union[bytes, bytearray]) -> int:  # type: ignore[override]
        raise TypeError


@_register_async_io_proxy_cls
class TypingTextIO_AsyncIoProxy(TypingIO_AsyncIoProxy[str], proxied_cls=ta.TextIO):  # noqa
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
