import typing as ta
import types
import weakref


T = ta.TypeVar('T')


##


_STATIC_VALUES: ta.MutableMapping[types.CodeType, ta.Callable] = weakref.WeakKeyDictionary()


def static(fn: ta.Callable[[], T]) -> T:
    try:
        return _STATIC_VALUES[fn.__code__]  # noqa
    except KeyError:
        pass

    _STATIC_VALUES[fn.__code__] = v = fn()  # noqa
    return v


def _main() -> None:
    for _ in range(3):
        print(static(lambda: (print('hi!'), 420)))


if __name__ == '__main__':
    _main()
