import functools
import typing as ta

from .base import AsyncLifecycle
from .base import Lifecycle
from .managed import AsyncLifecycleManaged
from .managed import LifecycleManaged


##


@functools.singledispatch
def unwrap_lifecycle(obj: ta.Any) -> Lifecycle | None:
    return None


@unwrap_lifecycle.register
def _(obj: Lifecycle) -> Lifecycle:
    return obj


@unwrap_lifecycle.register
def _(obj: LifecycleManaged) -> Lifecycle:
    return obj._lifecycle  # noqa


#


@functools.singledispatch
def unwrap_async_lifecycle(obj: ta.Any) -> AsyncLifecycle | None:
    return None


@unwrap_async_lifecycle.register
def _(obj: AsyncLifecycle) -> AsyncLifecycle:
    return obj


@unwrap_async_lifecycle.register
def _(obj: AsyncLifecycleManaged) -> AsyncLifecycle:
    return obj._lifecycle  # noqa


#


def unwrap_any_lifecycle(obj: ta.Any) -> Lifecycle | AsyncLifecycle | None:
    if (lc := unwrap_lifecycle(obj)) is not None:
        return lc

    elif (alc := unwrap_async_lifecycle(obj)) is not None:
        return alc

    else:
        return None
