import inspect
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from .types import Tag


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class Key(lang.Final, ta.Generic[T]):
    ty: rfl.Type = dc.xfield(coerce=rfl.typeof)

    _: dc.KW_ONLY

    tag: ta.Any = dc.xfield(
        default=None,
        validate=lambda o: not isinstance(o, Tag),
        repr_fn=lang.opt_repr,
    )


##


class TAG_NOT_SET(lang.Marker):  # noqa
    pass


@ta.overload
def as_key(o: Key[T]) -> Key[T]:
    ...


@ta.overload
def as_key(o: type[T], *, tag: ta.Any | type[TAG_NOT_SET] = type[TAG_NOT_SET]) -> Key[T]:
    ...


@ta.overload
def as_key(o: ta.Any, *, tag: ta.Any | type[TAG_NOT_SET] = type[TAG_NOT_SET]) -> Key:
    ...


def as_key(o, *, tag=TAG_NOT_SET):
    if isinstance(o, Key):
        if tag is not TAG_NOT_SET:
            raise TypeError(f'Cannot specify tag {tag!r} for existing Key instance {o!r}')
        return o

    if o is None or o is inspect.Parameter.empty:
        raise TypeError(o)

    return Key(rfl.typeof(o), tag=tag if tag is not TAG_NOT_SET else None)
