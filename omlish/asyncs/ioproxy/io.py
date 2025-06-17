# ruff: noqa: UP006 UP007 UP045
import io
import typing as ta

from .proxy import AsyncIoProxy
from .proxy import _register_async_io_proxy_cls


SelfT = ta.TypeVar('SelfT')


##


@_register_async_io_proxy_cls
class IOBase_AsyncIoProxy(AsyncIoProxy, proxied_cls=io.IOBase):  # noqa
    # https://github.com/python/cpython/blob/e65a1eb93ae35f9fbab1508606e3fbc89123629f/Lib/_pyio.py#L305

    ##
    # Positioning

    async def seek(self, pos, whence=0):
        raise TypeError

    async def tell(self):
        raise TypeError

    async def truncate(self, pos=None):
        raise TypeError

    ##
    # Flush and close

    async def flush(self):
        raise TypeError

    async def close(self):
        raise TypeError

    ##
    # Inquiries

    def seekable(self):
        raise TypeError

    def readable(self):
        raise TypeError

    def writable(self):
        raise TypeError

    @property
    def closed(self):
        raise TypeError

    ##
    # Context manager

    async def __aenter__(self: SelfT) -> SelfT:
        raise TypeError

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        raise TypeError

    ##
    # Lower-level APIs

    def fileno(self):
        raise TypeError

    def isatty(self):
        raise TypeError

    ##
    # Readline[s] and writelines

    async def readline(self, size=-1):
        raise TypeError

    # def __iter__(self):
    #     raise TypeError

    # def __next__(self):
    #     raise TypeError

    async def readlines(self, hint=None):
        raise TypeError

    async def writelines(self, lines):
        raise TypeError


@_register_async_io_proxy_cls
class RawIOBase_AsyncIoProxy(IOBase_AsyncIoProxy, proxied_cls=io.RawIOBase):  # noqa
    async def read(self, size=-1):
        raise TypeError

    async def readall(self):
        raise TypeError

    async def readinto(self, b):
        raise TypeError

    async def write(self, b):
        raise TypeError


@_register_async_io_proxy_cls
class BufferedIOBase_AsyncIoProxy(IOBase_AsyncIoProxy, proxied_cls=io.BufferedIOBase):  # noqa
    async def read(self, size=-1):
        raise TypeError

    async def read1(self, size=-1):
        raise TypeError

    async def readinto(self, b):
        raise TypeError

    async def readinto1(self, b):
        raise TypeError

    async def write(self, b):
        raise TypeError

    async def detach(self):
        raise TypeError


class BufferedIOMixin_AsyncIoProxy(BufferedIOBase_AsyncIoProxy):  # noqa
    @property
    def raw(self):
        raise TypeError

    @property
    def name(self):
        raise TypeError

    @property
    def mode(self):
        raise TypeError


@_register_async_io_proxy_cls
class BytesIO_AsyncIoProxy(BufferedIOBase_AsyncIoProxy, proxied_cls=io.BytesIO):  # noqa
    async def getvalue(self):
        raise TypeError

    async def getbuffer(self):
        raise TypeError


@_register_async_io_proxy_cls
class BufferedReader_AsyncIoProxy(BufferedIOMixin_AsyncIoProxy, proxied_cls=io.BufferedReader):  # noqa
    async def peek(self, size=0):
        raise TypeError


@_register_async_io_proxy_cls
class BufferedWriter_AsyncIoProxy(BufferedIOMixin_AsyncIoProxy, proxied_cls=io.BufferedWriter):  # noqa
    pass


@_register_async_io_proxy_cls
class BufferedRWPair_AsyncIoProxy(BufferedIOBase_AsyncIoProxy, proxied_cls=io.BufferedRWPair):  # noqa
    async def peek(self, size=0):
        raise TypeError


@_register_async_io_proxy_cls
class BufferedRandom_AsyncIoProxy(BufferedWriter_AsyncIoProxy, BufferedReader_AsyncIoProxy, proxied_cls=io.BufferedRandom):  # noqa
    pass


@_register_async_io_proxy_cls
class FileIO_AsyncIoProxy(RawIOBase_AsyncIoProxy, proxied_cls=io.FileIO):  # noqa
    @property
    def closefd(self):
        raise TypeError

    @property
    def mode(self):
        raise TypeError


@_register_async_io_proxy_cls
class TextIOBase_AsyncIoProxy(IOBase_AsyncIoProxy, proxied_cls=io.TextIOBase):  # noqa
    async def read(self, size=-1):
        raise TypeError

    async def write(self, s):
        raise TypeError

    async def detach(self):
        raise TypeError

    @property
    def encoding(self):
        raise TypeError

    @property
    def newlines(self):
        raise TypeError

    @property
    def errors(self):
        raise TypeError


@_register_async_io_proxy_cls
class TextIOWrapper_AsyncIoProxy(TextIOBase_AsyncIoProxy, proxied_cls=io.TextIOWrapper):  # noqa
    @property
    def line_buffering(self):
        raise TypeError

    @property
    def write_through(self):
        raise TypeError

    @property
    def buffer(self):
        raise TypeError

    async def reconfigure(
            self,
            *,
            encoding=None,
            errors=None,
            newline=Ellipsis,
            line_buffering=None,
            write_through=None,
    ):
        raise TypeError

    @property
    def name(self):
        raise TypeError


@_register_async_io_proxy_cls
class StringIO_AsyncIoProxy(TextIOWrapper_AsyncIoProxy, proxied_cls=io.StringIO):  # noqa
    async def getvalue(self):
        raise TypeError
