import collections
import dataclasses as dc
import types
import typing as ta

from .. import check


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

    def __ror__(self, other: dc.Field) -> dc.Field:
        return self(other)

    def __call__(self, f: dc.Field) -> dc.Field:
        return check.isinstance(self.fn(check.isinstance(f, dc.Field)), dc.Field)


def chain_metadata(*mds: ta.Mapping) -> types.MappingProxyType:
    return types.MappingProxyType(collections.ChainMap(*mds))  # type: ignore  # noqa


def update_field_metadata(f: dc.Field, nmd: ta.Mapping) -> dc.Field:
    check.isinstance(f, dc.Field)
    f.metadata = chain_metadata(nmd, f.metadata)
    return f
