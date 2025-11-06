"""
TODO:
 - more aggressive import metapath hook to forbid early imports
 - mode to make main thread the executor? :/
"""
import concurrent.futures as cf
import sys
import threading
import typing as ta

from omlish import lang

from ..dtx import DedicatedThreadExecutor


T = ta.TypeVar('T')
P = ta.ParamSpec('P')

O = ta.TypeVar('O')
I = ta.TypeVar('I')
R = ta.TypeVar('R')


##


@ta.final
class TinygradExecutor(DedicatedThreadExecutor, lang.Final):
    def __init__(
            self,
            *,
            daemon: bool = True,
    ) -> None:
        super().__init__(daemon=daemon)

        self.add_startup_callback(self._import_tinygrad)

    #

    class AlreadyImportedError(Exception):
        pass

    def _check_not_imported(self) -> None:
        if 'tinygrad' in sys.modules:
            raise TinygradExecutor.AlreadyImportedError('tinygrad already imported')

    def _pre_start(self) -> None:
        self._check_not_imported()

    def _import_tinygrad(self) -> None:
        self._check_not_imported()

        import tinygrad  # noqa


##


_GLOBAL_LOCK = threading.RLock()
_GLOBAL_EXECUTOR: TinygradExecutor


def get_or_make_executor() -> TinygradExecutor:
    global _GLOBAL_EXECUTOR

    try:
        return _GLOBAL_EXECUTOR
    except NameError:
        pass

    with _GLOBAL_LOCK:
        try:
            return _GLOBAL_EXECUTOR
        except NameError:
            pass

        _GLOBAL_EXECUTOR = TinygradExecutor()

        return _GLOBAL_EXECUTOR


def get_executor() -> TinygradExecutor:
    try:
        return _GLOBAL_EXECUTOR
    except NameError:
        raise TinygradExecutor.NotRunningError


#


def submit(fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> cf.Future[T]:
    return get_executor().submit(fn, *args, **kwargs)


def call(fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    return get_executor().call(fn, *args, **kwargs)


def call_gen(
        fn: ta.Callable[P, ta.Generator[O, I, R]],
        *args: P.args,
        **kwargs: P.kwargs,
) -> ta.Generator[O, I, R]:
    return get_executor().call_gen(fn, *args, **kwargs)
