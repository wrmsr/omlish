import functools
import os.path  # noqa
import pprint
import typing as ta  # noqa


########################################
# /Users/spinlock/src/wrmsr/omlish/x/amalg/demo/std/cached.py


class cached_nullary:  # noqa
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value

    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


########################################
# /Users/spinlock/src/wrmsr/omlish/x/amalg/demo/std/check.py


T = ta.TypeVar('T')


def check_not_none(v: ta.Optional[T]) -> T:  # noqa
    if v is None:
        raise ValueError
    return v


def check_not(v: ta.Any) -> None:
    if v:
        raise ValueError(v)
    return v


########################################
# /Users/spinlock/src/wrmsr/omlish/x/amalg/demo/demo.py


@cached_nullary
def _foo():
    return 5


def _main() -> None:
    """Docstring"""

    # Comment
    check_not_none(_foo())  # Inline comment

    pprint.pprint('hi')


if __name__ == '__main__':
    _main()
