# ruff: noqa: UP006 UP007
import dataclasses as dc
import functools
import inspect
import typing as ta

from omlish.lite.check import check


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
def async_io_proxy_cls_for(obj: ta.Any) -> ta.Type[AsyncIoProxy]:
    raise TypeError(obj)


def _register_async_io_proxy_cls(cls):
    async_io_proxy_cls_for.register(
        check.isinstance(cls.__dict__['__proxied_cls__'], type),
        lambda obj: cls,
    )
    return cls
