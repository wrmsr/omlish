# ruff: noqa: UP006 UP007
import io

from .proxy import AsyncIoProxy
from .proxy import _register_async_io_proxy_cls


##


@_register_async_io_proxy_cls
class IOBaseAsyncIoProxy(AsyncIoProxy, proxied_cls=io.IOBase):
    # https://github.com/python/cpython/blob/e65a1eb93ae35f9fbab1508606e3fbc89123629f/Lib/_pyio.py#L305

    ### Positioning ###

    async def seek(self, pos, whence=0):
        raise TypeError

    async def tell(self):
        raise TypeError

    async def truncate(self, pos=None):
        raise TypeError

    ### Flush and close ###

    async def flush(self):
        raise TypeError

    async def close(self):
        raise TypeError

    ### Inquiries ###

    def seekable(self):
        raise TypeError

    def readable(self):
        raise TypeError

    def writable(self):
        raise TypeError

    @property
    def closed(self):
        raise TypeError

    ### Context manager ###

    async def __aenter__(self):
        raise TypeError

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        raise TypeError

    ### Lower-level APIs ###

    def fileno(self):
        raise TypeError

    def isatty(self):
        raise TypeError

    ### Readline[s] and writelines ###

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
class RawIOBaseAsyncIoProxy(IOBaseAsyncIoProxy, proxied_cls=io.RawIOBase):
    async def read(self, size=-1):
        raise TypeError

    async def readall(self):
        raise TypeError

    async def readinto(self, b):
        raise TypeError

    async def write(self, b):
        raise TypeError


@_register_async_io_proxy_cls
class BufferedIOBaseAsyncIoProxy(IOBaseAsyncIoProxy, proxied_cls=io.BufferedIOBase):
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


class BufferedIOMixinAsyncIoProxy(BufferedIOBaseAsyncIoProxy):
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
class BytesIOAsyncIoProxy(BufferedIOBaseAsyncIoProxy, proxied_cls=io.BytesIO):
    async def getvalue(self):
        raise TypeError

    async def getbuffer(self):
        raise TypeError


@_register_async_io_proxy_cls
class BufferedReaderAsyncIoProxy(BufferedIOMixinAsyncIoProxy, proxied_cls=io.BufferedReader):
    async def peek(self, size=0):
        raise TypeError


@_register_async_io_proxy_cls
class BufferedWriterAsyncIoProxy(BufferedIOMixinAsyncIoProxy, proxied_cls=io.BufferedWriter):
    pass


@_register_async_io_proxy_cls
class BufferedRWPairAsyncIoProxy(BufferedIOBaseAsyncIoProxy, proxied_cls=io.BufferedRWPair):
    async def peek(self, size=0):
        raise TypeError


@_register_async_io_proxy_cls
class BufferedRandomAsyncIoProxy(BufferedWriterAsyncIoProxy, BufferedReaderAsyncIoProxy, proxied_cls=io.BufferedRandom):
    pass


@_register_async_io_proxy_cls
class FileIOAsyncIoProxy(RawIOBaseAsyncIoProxy, proxied_cls=io.FileIO):
    @property
    def closefd(self):
        raise TypeError

    @property
    def mode(self):
        raise TypeError


@_register_async_io_proxy_cls
class TextIOBaseAsyncIoProxy(IOBaseAsyncIoProxy, proxied_cls=io.TextIOBase):
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
class TextIOWrapperAsyncIoProxy(TextIOBaseAsyncIoProxy, proxied_cls=io.TextIOWrapper):
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
class StringIOAsyncIoProxy(TextIOWrapperAsyncIoProxy, proxied_cls=io.StringIO):
    async def getvalue(self):
        raise TypeError
