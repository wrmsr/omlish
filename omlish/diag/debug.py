"""
TODO:
 - select best debugger: ipdb, pudb,
"""
import dataclasses as dc
import functools
import traceback
import types
import typing as ta

from .. import check
from .. import lang


if ta.TYPE_CHECKING:
    import pdb  # noqa

    from . import pydevd

else:
    pdb = lang.proxy_import('pdb')

    pydevd = lang.proxy_import('.pydevd', __package__)


T = ta.TypeVar('T')
P = ta.ParamSpec('P')

ExceptionInfo: ta.TypeAlias = tuple[type[BaseException], BaseException, types.TracebackType]

PostMortemDebugger: ta.TypeAlias = ta.Callable[[ExceptionInfo], None]


##


def pdb_post_mortem_debugger(ei: ExceptionInfo) -> None:
    pdb.post_mortem(ei[2])


def get_post_mortem_debugger() -> PostMortemDebugger:
    if pydevd.is_present():
        return pydevd.debug_unhandled_exception

    else:
        check.not_none(pdb.post_mortem)
        return pdb_post_mortem_debugger


##


@dc.dataclass(kw_only=True)
class DebuggingOnException:
    silent: bool = False

    fn: PostMortemDebugger | None = None

    def __call__(self, fn: ta.Callable[P, T]) -> ta.Callable[P, T]:
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)

        return inner

    def __enter__(self) -> ta.Self:
        if self.fn is None:
            self.fn = get_post_mortem_debugger()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            return

        if not self.silent:
            traceback.print_exc()

        check.not_none(self.fn)((exc_type, exc_val, exc_tb))


debugging_on_exception = DebuggingOnException
