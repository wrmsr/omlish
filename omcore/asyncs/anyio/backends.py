import typing as ta

import anyio

from .utils import get_current_task


##


BackendTask: ta.TypeAlias = ta.Union[  # noqa
    # asyncio.tasks.Task,
    # trio.lowlevel.Task,
    ta.Any,
]


def _is_class_named(obj: ta.Any, m: str, n: str) -> bool:
    cls = obj.__class__
    return cls.__module__ == m and cls.__name__ == n


def get_backend_task(at: anyio.TaskInfo) -> BackendTask | None:
    if _is_class_named(at, 'anyio._backends._asyncio', 'AsyncIOTaskInfo'):
        # https://github.com/agronholm/anyio/blob/8907964926a24461840eee0925d3f355e729f15d/src/anyio/_backends/_asyncio.py#L1846  # noqa
        # weakref.ref
        obj = at._task()  # type: ignore  # noqa
        if obj is not None and not (
                _is_class_named(obj, '_asyncio', 'Task') or
                _is_class_named(obj, 'asyncio.tasks', 'Task')
        ):
            raise TypeError(obj)
        return obj

    elif _is_class_named(at, 'anyio._backends._trio', 'TrioTaskInfo'):
        # https://github.com/agronholm/anyio/blob/8907964926a24461840eee0925d3f355e729f15d/src/anyio/_backends/_trio.py#L850  # noqa
        # weakref.proxy
        # https://stackoverflow.com/a/62144308 :|
        obj = at._task.__repr__.__self__  # type: ignore  # noqa
        if obj is not None and not _is_class_named(obj, 'trio.lowlevel', 'Task'):
            raise TypeError(obj)
        return obj

    else:
        raise TypeError(at)


def get_current_backend_task() -> BackendTask | None:
    if (at := get_current_task()) is not None:
        return get_backend_task(at)
    else:
        return None
