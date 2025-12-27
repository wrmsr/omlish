import dataclasses as dc
import operator
import typing as ta


T = ta.TypeVar('T')


##


def deep_replace(o: T, *args: str | ta.Callable[[ta.Any], ta.Mapping[str, ta.Any]]) -> T:
    if not args:
        return o
    elif len(args) == 1:
        return dc.replace(o, **args[0](o))  # type: ignore
    else:
        return dc.replace(o, **{args[0]: deep_replace(getattr(o, args[0]), *args[1:])})  # type: ignore


##


def replace_if(
        o: T,
        fn: ta.Callable[[ta.Any, ta.Any], bool] = operator.eq,
        /,
        **kwargs: ta.Any,
) -> T:
    dct: dict[str, ta.Any] = {}
    for k, v in kwargs.items():
        if fn(getattr(o, k), v):
            dct[k] = v  # noqa
    if not dct:
        return o
    return dc.replace(o, **dct)  # type: ignore


def replace_ne(o: T, **kwargs: ta.Any) -> T:
    return replace_if(o, operator.ne, **kwargs)


def replace_is_not(o: T, **kwargs: ta.Any) -> T:
    return replace_if(o, operator.is_not, **kwargs)
