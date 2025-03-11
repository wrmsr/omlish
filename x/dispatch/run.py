import glob
import os.path
import shutil
import time
import typing as ta

from omdev.cexts import importhook
from omlish.dispatch.impls import find_impl as default_find_impl


T = ta.TypeVar('T')


def _main() -> None:
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)

    importhook.install()

    #

    # from . import _claude as _dispatch  # noqa
    from . import _gpto1 as _dispatch  # noqa
    # from omlish import dispatch as _dispatch

    #

    class Dispatcher(ta.Generic[T]):
        def __init__(self, find_impl: ta.Callable[[type, ta.Mapping[type, T]], T | None] | None = None) -> None:
            super().__init__()

            if find_impl is None:
                find_impl = default_find_impl
            self._x = _dispatch.Dispatcher(find_impl)

        def cache_size(self) -> int:
            return self._x.cache_size()

        def dispatch(self, cls: type) -> T | None:
            return self._x.dispatch(cls)

        def register(self, impl: T, cls_col: ta.Iterable[type]) -> T:
            return self._x.register(impl, cls_col)

    #

    disp = Dispatcher()
    disp.register('object', [object])
    disp.register('str', [str])
    disp_dispatch = disp.dispatch

    n = 1_000_000
    start = time.time_ns()

    for _ in range(n):
        disp_dispatch(str)

    end = time.time_ns()
    total = end - start
    per = total / n
    print(f'{per} ns / it')

    #

    importhook.uninstall()


if __name__ == '__main__':
    _main()
