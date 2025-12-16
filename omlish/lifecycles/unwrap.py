import typing as ta

from .base import AsyncLifecycle
from .base import Lifecycle
from .managed import AsyncLifecycleManaged
from .managed import LifecycleManaged


##


def unwrap_lifecycle(obj: ta.Any) -> Lifecycle | None:
    if isinstance(obj, Lifecycle):
        return obj

    elif isinstance(obj, LifecycleManaged):
        return obj._lifecycle  # noqa

    else:
        return None


def unwrap_async_lifecycle(obj: ta.Any) -> AsyncLifecycle | None:
    if isinstance(obj, AsyncLifecycle):
        return obj

    elif isinstance(obj, AsyncLifecycleManaged):
        return obj._lifecycle  # noqa

    else:
        return None


def unwrap_any_lifecycle(obj: ta.Any) -> Lifecycle | AsyncLifecycle | None:
    if (lc := unwrap_lifecycle(obj)) is not None:
        return lc

    elif (alc := unwrap_async_lifecycle(obj)) is not None:
        return alc

    else:
        return None
