import typing as ta

from .lite.check import CheckArgsRenderer as ArgsRenderer  # noqa
from .lite.check import CheckExceptionFactory as ExceptionFactory  # noqa
from .lite.check import CheckLateConfigureFn as LateConfigureFn  # noqa
from .lite.check import CheckMessage as Message  # noqa
from .lite.check import CheckOnRaiseFn as OnRaiseFn  # noqa
from .lite.check import Checks
from .lite.check import check


_isinstance = isinstance
_issubclass = issubclass
_callable = callable


##


register_on_raise = check.register_on_raise
unregister_on_raise = check.unregister_on_raise


##


def _try_get_args_rendering() -> ArgsRenderer | None:
    try:
        from .diag.asts import ArgsRenderer

        ArgsRenderer.smoketest()

    except Exception:  # noqa
        return None

    def _real_render_args(fmt: str, *args: ta.Any) -> str | None:
        ra = ArgsRenderer(back=3).render_args(*args)
        if ra is None:
            return None

        return fmt % tuple(str(a) for a in ra)

    return _real_render_args


def _try_enable_args_rendering(c: Checks) -> None:
    if (rf := _try_get_args_rendering()) is not None:
        c.set_args_renderer(rf)


check.register_late_configure(_try_enable_args_rendering)


##


isinstance = check.isinstance  # noqa
of_isinstance = check.of_isinstance
cast = check.cast
of_cast = check.of_cast
not_isinstance = check.not_isinstance
of_not_isinstance = check.of_not_isinstance

#

issubclass = check.issubclass  # noqa
not_issubclass = check.not_issubclass

#

in_ = check.in_
not_in = check.not_in
empty = check.empty
iterempty = check.iterempty
not_empty = check.not_empty
unique = check.unique
single = check.single
opt_single = check.opt_single

#

none = check.none
not_none = check.not_none

#

equal = check.equal
not_equal = check.not_equal
is_ = check.is_
is_not = check.is_not
callable = check.callable  # noqa
non_empty_str = check.non_empty_str
replacing = check.replacing
replacing_none = check.replacing_none

#

arg = check.arg
state = check.state
