import collections.abc
import typing as ta

from .iter import fields_dict


##


def _only_test(v: ta.Any) -> bool:
    if v is None:
        return False
    elif isinstance(v, collections.abc.Iterable):
        return bool(v)
    else:
        return True


def only(
        obj: ta.Any,
        *flds: str,
        all: bool = False,  # noqa
        test: ta.Callable[[ta.Any], bool] = _only_test,
) -> bool:
    fdct = fields_dict(obj)
    for fn in flds:
        if fn not in fdct:
            raise KeyError(fn)

    rem = set(flds)
    for fn, f in fdct.items():
        if not f.compare and fn not in rem:
            continue

        v = getattr(obj, fn)
        if test(v):
            if fn in rem:
                rem.remove(fn)
            else:
                return False

    if rem and all:
        return False

    return True
