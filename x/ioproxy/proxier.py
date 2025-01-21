# ruff: noqa: UP006 UP007
import abc
import io
import typing as ta

from .proxy import AsyncIoProxyTarget
from .proxy import async_io_proxy_cls_for

from .io import BufferedIOBaseAsyncIoProxy
from .io import BufferedRWPairAsyncIoProxy
from .io import BufferedRandomAsyncIoProxy
from .io import BufferedReaderAsyncIoProxy
from .io import BufferedWriterAsyncIoProxy
from .io import BytesIOAsyncIoProxy
from .io import FileIOAsyncIoProxy
from .io import IOBaseAsyncIoProxy
from .io import RawIOBaseAsyncIoProxy
from .io import StringIOAsyncIoProxy
from .io import TextIOBaseAsyncIoProxy
from .io import TextIOWrapperAsyncIoProxy
from .typing import TypingBinaryIOAsyncIoProxy
from .typing import TypingIOAsyncIoProxy
from .typing import TypingTextIOAsyncIoProxy


##


class AsyncIoProxier(abc.ABC):
    @ta.overload
    def proxy_obj(self, obj: io.IOBase) -> IOBaseAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.RawIOBase) -> RawIOBaseAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedIOBase) -> BufferedIOBaseAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BytesIO) -> BytesIOAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedReader) -> BufferedReaderAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedWriter) -> BufferedWriterAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedRWPair) -> BufferedRWPairAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedRandom) -> BufferedRandomAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.FileIO) -> FileIOAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.TextIOBase) -> TextIOBaseAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.TextIOWrapper) -> TextIOWrapperAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: io.StringIO) -> StringIOAsyncIoProxy:
        ...

    #

    @ta.overload
    def proxy_obj(self, obj: ta.IO) -> TypingIOAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: ta.BinaryIO) -> TypingBinaryIOAsyncIoProxy:
        ...

    @ta.overload
    def proxy_obj(self, obj: ta.TextIO) -> TypingTextIOAsyncIoProxy:
        ...

    #

    @abc.abstractmethod
    def target_obj(self, obj: ta.Any) -> AsyncIoProxyTarget:
        raise NotImplementedError

    @ta.final
    def proxy_obj(self, obj):
        target = self.target_obj(obj)
        proxy_cls = async_io_proxy_cls_for(obj)
        proxy = proxy_cls(target)
        return proxy

    ##

    # def proxy_fn(self, fn, *, wrap_result=False):

