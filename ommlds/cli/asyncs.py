import abc
import functools
import typing as ta

from omlish import lang


with lang.auto_proxy_import(globals()):
    import anyio


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class AsyncThreadRunner(lang.Abstract):
    @abc.abstractmethod
    def run_in_thread(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T]:
        raise NotImplementedError


##


class AnyioAsyncThreadRunner(AsyncThreadRunner):
    def run_in_thread(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T]:
        return anyio.to_thread.run_sync(functools.partial(fn, *args, **kwargs))
