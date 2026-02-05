import types
import typing as ta
import weakref


T = ta.TypeVar('T')


##


_STATIC_VALUES: ta.MutableMapping[types.CodeType, ta.Any] = weakref.WeakKeyDictionary()


def static(fn: ta.Callable[[], T]) -> T:
    try:
        return _STATIC_VALUES[fn.__code__]  # noqa
    except KeyError:
        pass

    _STATIC_VALUES[fn.__code__] = v = fn()  # noqa
    return v
