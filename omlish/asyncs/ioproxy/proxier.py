# ruff: noqa: UP006 UP007
import io
import types
import typing as ta

from .io import BufferedIOBase_AsyncIoProxy
from .io import BufferedRandom_AsyncIoProxy
from .io import BufferedReader_AsyncIoProxy
from .io import BufferedRWPair_AsyncIoProxy
from .io import BufferedWriter_AsyncIoProxy
from .io import BytesIO_AsyncIoProxy
from .io import FileIO_AsyncIoProxy
from .io import IOBase_AsyncIoProxy
from .io import RawIOBase_AsyncIoProxy
from .io import StringIO_AsyncIoProxy
from .io import TextIOBase_AsyncIoProxy
from .io import TextIOWrapper_AsyncIoProxy
from .proxy import AsyncIoProxyRunner
from .proxy import AsyncIoProxyTarget
from .proxy import async_io_proxy_cls_for
from .proxy import async_io_proxy_fn
from .typing import TypingBinaryIO_AsyncIoProxy
from .typing import TypingIO_AsyncIoProxy
from .typing import TypingTextIO_AsyncIoProxy


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

    def proxy_obj_with_cls(self, obj, proxy_cls):
        target = self.target_obj(obj)
        proxy = proxy_cls(target)
        return proxy

    def maybe_proxy_obj(self, obj):
        if (proxy_cls := async_io_proxy_cls_for(obj)) is None:
            return obj
        return self.proxy_obj_with_cls(obj, proxy_cls)

    ##

    @ta.overload
    def proxy_obj(self, obj: io.StringIO) -> StringIO_AsyncIoProxy:  # type: ignore[overload-overlap]  # 1
        ...

    @ta.overload
    def proxy_obj(self, obj: io.TextIOWrapper) -> TextIOWrapper_AsyncIoProxy:  # type: ignore[overload-overlap]  # 2
        ...

    @ta.overload
    def proxy_obj(self, obj: io.TextIOBase) -> TextIOBase_AsyncIoProxy:  # 3
        ...

    @ta.overload
    def proxy_obj(self, obj: io.FileIO) -> FileIO_AsyncIoProxy:  # type: ignore[overload-overlap]  # 4
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedRandom) -> BufferedRandom_AsyncIoProxy:  # type: ignore[overload-overlap]  # 5
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedRWPair) -> BufferedRWPair_AsyncIoProxy:  # 6
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedWriter) -> BufferedWriter_AsyncIoProxy:  # type: ignore[overload-overlap]  # 7
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedReader) -> BufferedReader_AsyncIoProxy:  # type: ignore[overload-overlap]  # 8
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BytesIO) -> BytesIO_AsyncIoProxy:  # type: ignore[overload-overlap]  # 9
        ...

    @ta.overload
    def proxy_obj(self, obj: io.BufferedIOBase) -> BufferedIOBase_AsyncIoProxy:  # 10
        ...

    @ta.overload
    def proxy_obj(self, obj: io.RawIOBase) -> RawIOBase_AsyncIoProxy:  # 11
        ...

    @ta.overload
    def proxy_obj(self, obj: io.IOBase) -> IOBase_AsyncIoProxy:  # 12
        ...

    #

    @ta.overload
    def proxy_obj(self, obj: ta.TextIO) -> TypingTextIO_AsyncIoProxy:  # 13
        ...

    @ta.overload
    def proxy_obj(self, obj: ta.BinaryIO) -> TypingBinaryIO_AsyncIoProxy:  # 14
        ...

    @ta.overload
    def proxy_obj(self, obj: ta.IO) -> TypingIO_AsyncIoProxy:  # 15
        ...

    #

    def proxy_obj(self, obj):
        if (proxy_cls := async_io_proxy_cls_for(obj)) is None:
            raise TypeError(obj)
        return self.proxy_obj_with_cls(obj, proxy_cls)

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
