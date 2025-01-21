"""
See: https://github.com/python/cpython/blob/e65a1eb93ae35f9fbab1508606e3fbc89123629f/Lib/_pyio.py
"""
import asyncio
import dataclasses as dc
import functools
import inspect
import io
import typing as ta

from omlish import check


AsyncIoProxyRunner: ta.TypeAlias = ta.Callable[[ta.Callable], ta.Any]


##


class AsyncIoProxy:
    @dc.dataclass(frozen=True)
    class _Target:
        obj: ta.Any
        runner: AsyncIoProxyRunner

    def __init__(self, *, _target: _Target) -> None:
        super().__init__()

        self._target = check.isinstance(_target, self._Target)

    #

    class _Descriptor:
        def __init__(self, name) -> None:
            super().__init__()

            self._name = name

        def __get__(self, instance, owner=None):
            if instance is None:
                return self

            target: AsyncIoProxy._Target = instance._target  # noqa
            v = self._get(target)
            setattr(instance, self._name, v)
            return v

        def _get(self, target: 'AsyncIoProxy._Target') -> ta.Any:
            raise NotImplementedError

    class _Property(_Descriptor):
        def _get(self, target: 'AsyncIoProxy._Target') -> ta.Any:
            return getattr(target.obj, self._name)

    class _Method(_Descriptor):
        def __call__(self, instance, *args, **kwargs):
            return self.__get__(instance)(*args, **kwargs)

    class _SyncMethod(_Method):
        def _get(self, target: 'AsyncIoProxy._Target') -> ta.Any:
            return getattr(target.obj, self._name)

    class _AsyncMethod(_Method):
        _WRAPPER_NAME_ATTRS = ('__name__', '__qualname__')
        _WRAPPER_ASSIGNMENTS = tuple(a for a in functools.WRAPPER_ASSIGNMENTS if a not in ('__name__', '__qualname__'))

        def _get(self, target: 'AsyncIoProxy._Target') -> ta.Any:
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


@ta.overload
def async_io_proxy(obj: io.IOBase, runner: AsyncIoProxyRunner) -> IOBaseAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.RawIOBase, runner: AsyncIoProxyRunner) -> RawIOBaseAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.BufferedIOBase, runner: AsyncIoProxyRunner) -> BufferedIOBaseAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.BytesIO, runner: AsyncIoProxyRunner) -> BytesIOAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.BufferedReader, runner: AsyncIoProxyRunner) -> BufferedReaderAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.BufferedWriter, runner: AsyncIoProxyRunner) -> BufferedWriterAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.BufferedRWPair, runner: AsyncIoProxyRunner) -> BufferedRWPairAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.BufferedRandom, runner: AsyncIoProxyRunner) -> BufferedRandomAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.FileIO, runner: AsyncIoProxyRunner) -> FileIOAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.TextIOBase, runner: AsyncIoProxyRunner) -> TextIOBaseAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.TextIOWrapper, runner: AsyncIoProxyRunner) -> TextIOWrapperAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: io.StringIO, runner: AsyncIoProxyRunner) -> StringIOAsyncIoProxy:
    ...


#


@ta.overload
def async_io_proxy(obj: ta.IO, runner: AsyncIoProxyRunner) -> RawIOBaseAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: ta.BinaryIO, runner: AsyncIoProxyRunner) -> RawIOBaseAsyncIoProxy:
    ...


@ta.overload
def async_io_proxy(obj: ta.TextIO, runner: AsyncIoProxyRunner) -> TextIOWrapperAsyncIoProxy:
    ...


#


def async_io_proxy(obj, runner):
    target = AsyncIoProxy._Target(  # noqa
        obj,
        runner,
    )

    proxy_cls = async_io_proxy_cls_for(obj)
    proxy = proxy_cls(_target=target)

    return proxy


##


async def _a_main() -> None:
    loop = asyncio.get_running_loop()
    runner = functools.partial(loop.run_in_executor, None)

    with open('pyproject.toml') as f:
        p = async_io_proxy(f, runner)
        print(p.fileno())
        print(await p.read())


if __name__ == '__main__':
    asyncio.run(_a_main())
