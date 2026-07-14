import contextlib
import typing as ta

from omcore import lang
from omcore.inject.binder import bind
from omcore.inject.elements import Elemental
from omcore.inject.impl.inspect import build_kwargs_target


if ta.TYPE_CHECKING:
    from .. import maysync as _maysync
else:
    _maysync = lang.proxy_import('..maysync', __package__)


T = ta.TypeVar('T')


##


def create_maysync_managed_injector(*args: Elemental) -> ta.ContextManager[_maysync.MaysyncInjector]:
    @contextlib.contextmanager
    def inner():
        with contextlib.ExitStack() as es:
            yield _maysync.create_maysync_injector(
                bind(contextlib.ExitStack, to_const=es),
                *args,
            )
    return inner()


def make_maysync_managed_provider(
        fac: ta.Callable[..., T],
        *fns: ta.Callable[[T], ta.ContextManager[T]],
) -> ta.Callable[..., T]:
    kt = build_kwargs_target(fac)

    def _provide(
            i: _maysync.MaysyncInjector,
            es: contextlib.ExitStack,
    ):
        obj = i.inject(kt)
        if not fns:
            obj = es.enter_context(obj)
        else:
            for fn in fns:
                es.enter_context(fn(obj))
        return obj

    return _provide
