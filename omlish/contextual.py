# fmt: off
# ruff: noqa: I001
import typing as ta

from .lite.contextual import (  # noqa
    ContextualParams as Params,

    UnboundContextualError as UnboundError,
    NO_CONTEXTUAL_DEFAULT as NO_DEFAULT,
    is_unbound_contextual_param as is_unbound_param,

    contextual_param as param,

    ContextualParam as Param,
    inspect_contextual_params as inspect_params,

    contextual_wrap as _wrap,

    contextual_bind as bind,

    contextual_get as get,
)


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class Wrapping(ta.Protocol):
    @ta.overload
    def __call__(self, ty: type[T]) -> type[T]: ...

    @ta.overload
    def __call__(self, fn: ta.Callable[P, T]) -> ta.Callable[P, T]: ...


def wrap() -> Wrapping:
    return _wrap()
