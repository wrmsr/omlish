import abc
import asyncio
import contextlib
import dataclasses as dc
import functools
import inspect
import io
import typing as ta

from omlish import check


AnyStrT = ta.TypeVar('AnyStrT', bytes, str)

AsyncIoProxyRunner: ta.TypeAlias = ta.Callable[[ta.Callable], ta.Any]


##


@dc.dataclass(frozen=True)
class AsyncIoProxyTarget:
    obj: ta.Any
    runner: AsyncIoProxyRunner


class AsyncIoProxy:
    def __init__(self, target: AsyncIoProxyTarget) -> None:
        super().__init__()

        self._target = check.isinstance(target, AsyncIoProxyTarget)

    #

    class _Descriptor:
        def __init__(self, name) -> None:
            super().__init__()

            self._name = name

        def __get__(self, instance, owner=None):
            if instance is None:
                return self

            target: AsyncIoProxyTarget = instance._target  # noqa
            v = self._get(target)

            setattr(instance, self._name, v)
            return v

        def _get(self, target: AsyncIoProxyTarget) -> ta.Any:
            raise NotImplementedError

    class _Property(_Descriptor):
        def _get(self, target: AsyncIoProxyTarget) -> ta.Any:
            return getattr(target.obj, self._name)

    class _Method(_Descriptor):
        def __call__(self, instance, *args, **kwargs):
            return self.__get__(instance)(*args, **kwargs)

    class _SyncMethod(_Method):
        def _get(self, target: AsyncIoProxyTarget) -> ta.Any:
            return getattr(target.obj, self._name)

    class _AsyncMethod(_Method):
        _WRAPPER_NAME_ATTRS = ('__name__', '__qualname__')
        _WRAPPER_ASSIGNMENTS = tuple(a for a in functools.WRAPPER_ASSIGNMENTS if a not in ('__name__', '__qualname__'))

        def _get(self, target: AsyncIoProxyTarget) -> ta.Any:
            fn = getattr(target.obj, self._name)

            @functools.wraps(fn, assigned=self._WRAPPER_ASSIGNMENTS)
            async def run(*args, **kwargs):
                return await target.runner(functools.partial(fn, *args, **kwargs))

            for na in self._WRAPPER_NAME_ATTRS:
                setattr(run, na, f'{getattr(run, na)}:{getattr(fn, na)}')

            return run

    #

    def __init_subclass__(cls, *, proxied_cls=None, **kwargs):  # noqa
        super().__init_subclass__()

        cls.__proxied_cls__ = check.isinstance(proxied_cls, (type, None))

        for n, v in dict(cls.__dict__).items():
            if n.startswith('_'):
                continue

            if isinstance(v, property):
                setattr(cls, n, cls._Property(n))

            elif callable(v):
                if inspect.iscoroutinefunction(v):
                    setattr(cls, n, cls._AsyncMethod(n))
                else:
                    setattr(cls, n, cls._SyncMethod(n))

            else:
                raise TypeError(v)


##


@functools.singledispatch
def async_io_proxy_cls_for(obj: ta.Any) -> type[AsyncIoProxy]:
    raise TypeError(obj)


def _register_async_io_proxy_cls(cls):
    async_io_proxy_cls_for.register(
        check.isinstance(cls.__dict__['__proxied_cls__'], type),
        lambda obj: cls,
    )
    return cls


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

    # def __enter__(self):  # That's a forward reference
    #     raise TypeError

    # def __exit__(self, *args):
    #     raise TypeError

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

    async def readlines(self, hint: int = -1) -> list[AnyStrT]:
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

    async def writelines(self, lines: list[AnyStrT]) -> None:
        raise TypeError

    # def __enter__(self) -> 'IO[AnyStrT]':
    #     pass

    # def __exit__(self, type, value, traceback) -> None:
    #     pass


class TypingBinaryIOAsyncIoProxy(TypingIOAsyncIoProxy[bytes], proxied_cls=ta.BinaryIO):
    def write(self, s: bytes | bytearray) -> int:
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
    def errors(self) -> str | str:
        raise TypeError

    @property
    def line_buffering(self) -> bool:
        raise TypeError

    @property
    def newlines(self) -> ta.Any:
        raise TypeError

    # def __enter__(self) -> 'TextIO':
    #     pass


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


class AsyncioAsyncIoProxier(AsyncIoProxier):
    def __init__(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        super().__init__()

        self._loop = loop

    def get_loop(self) -> asyncio.AbstractEventLoop:
        if (l := self._loop) is not None:
            return l
        return asyncio.get_running_loop()

    def target_obj(self, obj: ta.Any) -> AsyncIoProxyTarget:
        loop = self.get_loop()
        runner = functools.partial(loop.run_in_executor, None)
        return AsyncIoProxyTarget(obj, runner)


ASYNCIO_ASYNC_IO_PROXIER = AsyncioAsyncIoProxier()

asyncio_io_proxy = ASYNCIO_ASYNC_IO_PROXIER.proxy_obj


##


class AsyncIoProxyContextManager:
    def __init__(self, target: AsyncIoProxyTarget) -> None:
        super().__init__()

        self._target = target

    async def __aenter__(self):
        await self._target.runner(self._target.obj.__enter__)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._target.runner(functools.partial(self._target.obj.__exit__, exc_type, exc_val, exc_tb))


@contextlib.asynccontextmanager
async def async_open(*args, **kwargs):
    loop = asyncio.get_running_loop()
    f = await loop.run_in_executor(None, functools.partial(open, *args, **kwargs))
    af = asyncio_io_proxy(f)
    # async with AsyncIoProxyContextManager(Async):
    try:
        yield af
    finally:
        await af.close()


async def _a_main() -> None:
    with open('pyproject.toml') as f:
        p = asyncio_io_proxy(f)
        print(p.fileno())
        print(await p.read())

    async with async_open('pyproject.toml') as af:
        print(af.fileno())
        print(await af.read())


if __name__ == '__main__':
    asyncio.run(_a_main())
