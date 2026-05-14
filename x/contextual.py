import typing as ta


from .contextual_lite import (  # noqa
    ContextualParams as Params,

    UnboundContextualParamError as UnboundParamError,
    NO_CONTEXTUAL_DEFAULT as NO_DEFAULT,
    contextual_param as param,

    ContextualParam as Param,
    inspect_contextual_params as inspect_params,

    contextual_wrap as _wrap,

    contextual_bind as bind,
)


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


def wrap() -> ta.Callable[[ta.Callable[P, T]], ta.Callable[P, T]]:
    return _wrap()
