import functools
import typing as ta

from .. import check
from .dispatch import Dispatcher
from .dispatch import get_impl_func_cls_set


def function(func):
    disp = Dispatcher()  # type: ignore
    disp.register(func, [object])

    func_name = getattr(func, '__name__', 'singledispatch function')
    disp_dispatch = disp.dispatch

    @functools.wraps(func)
    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f'{func_name} requires at least 1 positional argument')
        if (impl := disp_dispatch(type(args[0]))) is not None:
            return impl(*args, **kw)
        raise RuntimeError(f'No dispatch: {type(args[0])}')

    def register(impl, cls=None):
        check.callable(impl)
        cls_col: ta.Iterable[type]
        if cls is None:
            cls_col = get_impl_func_cls_set(impl)
        else:
            cls_col = frozenset([cls])
        disp.register(impl, cls_col)
        return impl

    wrapper.register = register  # type: ignore
    wrapper.dispatch = disp.dispatch  # type: ignore
    return wrapper
