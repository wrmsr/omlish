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
        fn: ta.Callable[[ta.Any, ta.Any], bool],
        o: T,
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
    return replace_if(operator.ne, o, **kwargs)


def replace_is_not(o: T, **kwargs: ta.Any) -> T:
    return replace_if(operator.is_not, o, **kwargs)


##


def merge_if(
        fn: ta.Callable[[ta.Any, ta.Any], bool],
        o: T,
        *os: T,
) -> T:
    odct = {f.name: getattr(o, f.name) for f in dc.fields(o)}  # type: ignore[arg-type]
    xdct: dict[str, ta.Any] = {}
    for x in reversed(os):
        if not odct:
            break
        if xu := {
            k: xv
            for k, ov in odct.items()
            if fn(ov, xv := getattr(x, k))
        }:
            xdct.update(xu)
            for k in xu:
                del odct[k]
    if not xdct:
        return o
    return dc.replace(o, **xdct)  # type: ignore


def merge_ne(o: T, *os: T) -> T:
    return merge_if(operator.ne, o, *os)


def merge_is_not(o: T, *os: T) -> T:
    return merge_if(operator.is_not, o,*os)
