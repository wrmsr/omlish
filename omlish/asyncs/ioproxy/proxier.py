# ruff: noqa: UP006 UP007
import io
import types
import typing as ta

from .io import BufferedIOBaseAsyncIoProxy
from .io import BufferedRandomAsyncIoProxy
from .io import BufferedReaderAsyncIoProxy
from .io import BufferedRWPairAsyncIoProxy
from .io import BufferedWriterAsyncIoProxy
from .io import BytesIOAsyncIoProxy
from .io import FileIOAsyncIoProxy
from .io import IOBaseAsyncIoProxy
from .io import RawIOBaseAsyncIoProxy
from .io import StringIOAsyncIoProxy
from .io import TextIOBaseAsyncIoProxy
from .io import TextIOWrapperAsyncIoProxy
from .proxy import AsyncIoProxyRunner
from .proxy import AsyncIoProxyTarget
from .proxy import async_io_proxy_cls_for
from .proxy import async_io_proxy_fn
from .typing import TypingBinaryIOAsyncIoProxy
from .typing import TypingIOAsyncIoProxy
from .typing import TypingTextIOAsyncIoProxy


##


@ta.final
class AsyncIoProxier:
    def __init__(self, runner_policy: ta.Callable[[ta.Any], AsyncIoProxyRunner]) -> None:
        super().__init__()

        self._runner_policy = runner_policy

    def get_runner(self, obj: ta.Any) -> AsyncIoProxyRunner:
        return self._runner_policy(obj)

    ##

    def target_obj(self, obj: ta.Any) -> AsyncIoProxyTarget:
        runner = self.get_runner(obj)
        return AsyncIoProxyTarget(obj, runner)

    #

    @ta.overload
    def proxy_obj(self, obj: io.StringIO) -> StringIOAsyncIoProxy:  # type: ignore[overload-overlap]  # 1
        ...

    @ta.overload
    def proxy_obj(self, obj: io.TextIOWrapper) -> TextIOWrapperAsyncIoProxy:  # type: ignore[overload-overlap]  # 2
        ...

    @ta.overload
    def proxy_obj(self, obj: io.TextIOBase) -> TextIOBaseAsyncIoProxy:  # 3
        ...

    @ta.overload
    def proxy_obj(self, obj: io.FileIO) -> FileIOAsyncIoProxy:  # type: ignore[overload-overlap]  # 4
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedRandom) -> BufferedRandomAsyncIoProxy:  # type: ignore[overload-overlap]  # 5
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedRWPair) -> BufferedRWPairAsyncIoProxy:  # 6
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedWriter) -> BufferedWriterAsyncIoProxy:  # type: ignore[overload-overlap]  # 7
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedReader) -> BufferedReaderAsyncIoProxy:  # type: ignore[overload-overlap]  # 8
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BytesIO) -> BytesIOAsyncIoProxy:  # type: ignore[overload-overlap]  # 9
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedIOBase) -> BufferedIOBaseAsyncIoProxy:  # 10
        ...

    @ta.overload
    def proxy_obj(self, obj: io.RawIOBase) -> RawIOBaseAsyncIoProxy:  # 11
        ...

    @ta.overload
    def proxy_obj(self, obj: io.IOBase) -> IOBaseAsyncIoProxy:  # 12
        ...

    #

    @ta.overload
    def proxy_obj(self, obj: ta.TextIO) -> TypingTextIOAsyncIoProxy:  # 13
        ...

    @ta.overload
    def proxy_obj(self, obj: ta.BinaryIO) -> TypingBinaryIOAsyncIoProxy:  # 14
        ...

    @ta.overload
    def proxy_obj(self, obj: ta.IO) -> TypingIOAsyncIoProxy:  # 15
        ...

    #

    def proxy_obj(self, obj):
        target = self.target_obj(obj)
        if (proxy_cls := async_io_proxy_cls_for(obj)) is None:
            raise TypeError(obj)
        proxy = proxy_cls(target)
        return proxy

    #

    def maybe_proxy_obj(self, obj):
        target = self.target_obj(obj)
        if (proxy_cls := async_io_proxy_cls_for(obj)) is None:
            return obj
        proxy = proxy_cls(target)
        return proxy

    ##

    def proxy_fn(self, fn, *, wrap_result='auto'):
        if wrap_result == 'auto':
            result_wrapper = self.maybe_proxy_obj
        elif wrap_result is True:
            result_wrapper = self.proxy_obj
        elif wrap_result is False:
            result_wrapper = None
        else:
            raise TypeError(wrap_result)
        runner = self.get_runner(fn)
        return async_io_proxy_fn(fn, runner, result_wrapper=result_wrapper)

    ##

    FN_TYPES: ta.Tuple[type, ...] = (
        types.BuiltinFunctionType,
        types.BuiltinMethodType,
        types.FunctionType,
        types.MethodType,
    )

    def proxy(self, obj):
        if isinstance(obj, self.FN_TYPES):
            return self.proxy_fn(obj)
        else:
            return self.proxy_obj(obj)
