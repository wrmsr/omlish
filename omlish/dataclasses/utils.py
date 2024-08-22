import collections
import dataclasses as dc
import types
import typing as ta

from .. import check
from .impl.params import DEFAULT_FIELD_EXTRAS
from .impl.params import FieldExtras
from .impl.params import get_field_extras


T = ta.TypeVar('T')


def maybe_post_init(sup: ta.Any) -> bool:
    try:
        fn = sup.__post_init__
    except AttributeError:
        return False
    fn()
    return True


def opt_repr(o: ta.Any) -> str | None:
    return repr(o) if o is not None else None


class field_modifier:  # noqa
    def __init__(self, fn: ta.Callable[[dc.Field], dc.Field]) -> None:
        super().__init__()
        self.fn = fn

    def __ror__(self, other: T) -> T:
        return self(other)

    def __call__(self, f: T) -> T:
        return check.isinstance(self.fn(check.isinstance(f, dc.Field)), dc.Field)  # type: ignore


def chain_metadata(*mds: ta.Mapping) -> types.MappingProxyType:
    return types.MappingProxyType(collections.ChainMap(*mds))  # type: ignore  # noqa


def update_field_metadata(f: dc.Field, nmd: ta.Mapping) -> dc.Field:
    check.isinstance(f, dc.Field)
    f.metadata = chain_metadata(nmd, f.metadata)
    return f


def update_field_extras(f: dc.Field, *, unless_non_default: bool = False, **kwargs: ta.Any) -> dc.Field:
    fe = get_field_extras(f)
    return update_field_metadata(f, {
        FieldExtras: dc.replace(fe, **{
            k: v
            for k, v in kwargs.items()
            if not unless_non_default or v != getattr(DEFAULT_FIELD_EXTRAS, k)
        }),
    })


def deep_replace(o: T, *args: str | ta.Callable[[ta.Any], ta.Mapping[str, ta.Any]]) -> T:
    if not args:
        return o
    elif len(args) == 1:
        return dc.replace(o, **args[0](o))  # type: ignore
    else:
        return dc.replace(o, **{args[0]: deep_replace(getattr(o, args[0]), *args[1:])})  # type: ignore
