import inspect
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import reflect2 as rfl
from .types import Tag


T = ta.TypeVar('T')


##


class TAG_NOT_SET(lang.Marker):  # noqa
    pass


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class Key(lang.Final, ta.Generic[T]):
    rty: rfl.Type = dc.xfield(validate=lambda o: isinstance(o, rfl.Type))

    _: dc.KW_ONLY

    tag: ta.Any = dc.xfield(
        default=None,
        validate=lambda o: not isinstance(o, Tag) and o is not TAG_NOT_SET,
        repr_fn=lang.opt_repr,
    )

    #

    # _rtk: rfl.TypeKey
    # _hash: int

    @property
    def rtk(self) -> rfl.TypeKey:
        return getattr(self, '_rtk')

    def __post_init__(self) -> None:
        object.__setattr__(self, '_rtk', self.rty.type_key())

    def __hash__(self) -> int:
        try:
            return getattr(self, '_hash')
        except AttributeError:
            pass

        h = hash((
            self._rtk,  # type: ignore[attr-defined]
            self.tag,
        ))

        object.__setattr__(self, '_hash', h)
        return h

    def __eq__(self, o: object) -> bool:
        if self is o:
            return True
        if self.__class__ is not o.__class__:
            return NotImplemented

        return (
            self._rtk == o._rtk and  # type: ignore[attr-defined]
            self.tag == o.tag  # noqa
        )


##


@ta.overload
def as_key(o: Key[T], *, tag: type[TAG_NOT_SET] = TAG_NOT_SET) -> Key[T]:
    ...


@ta.overload
def as_key(o: type[T], *, tag: ta.Any | type[TAG_NOT_SET] = TAG_NOT_SET) -> Key[T]:
    ...


@ta.overload
def as_key(o: ta.Any, *, tag: ta.Any | type[TAG_NOT_SET] = TAG_NOT_SET) -> Key:
    ...


def as_key(o, *, tag=TAG_NOT_SET):
    if isinstance(o, Key):
        if tag is not TAG_NOT_SET:
            raise TypeError(f'Cannot specify tag {tag!r} for existing Key instance {o!r}')
        return o

    if o is None or o is inspect.Parameter.empty:
        raise TypeError(o)

    return Key(rfl.reflect_type(o), tag=tag if tag is not TAG_NOT_SET else None)
