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
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def __ror__(self, other: dc.Field) -> dc.Field:
        return self(other)

    def __call__(self, f: dc.Field) -> dc.Field:
        return check.isinstance(self.fn(check.isinstance(f, dc.Field)), dc.Field)


def update_metadata(old: ta.Mapping, new: ta.Mapping) -> types.MappingProxyType:
    return types.MappingProxyType(collections.ChainMap(new, old))  # type: ignore  # noqa
