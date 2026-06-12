import typing as ta


T = ta.TypeVar('T')


##


def mypyc_attr(*args: ta.Any, **kwargs: ta.Any) -> ta.Callable[[T], T]:
    def inner(cls):
        return cls
    return inner


def trait(cls: T) -> T:
    return cls
