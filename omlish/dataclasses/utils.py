import collections
import dataclasses as dc
import types
import typing as ta

from .. import check
from .impl.metadata import METADATA_ATTR
from .impl.metadata import UserMetadata
from .impl.params import DEFAULT_FIELD_EXTRAS
from .impl.params import FieldExtras
from .impl.params import get_field_extras


T = ta.TypeVar('T')


#


def maybe_post_init(sup: ta.Any) -> bool:
    try:
        fn = sup.__post_init__
    except AttributeError:
        return False
    fn()
    return True


#


def opt_repr(o: ta.Any) -> str | None:
    return repr(o) if o is not None else None


def truthy_repr(o: ta.Any) -> str | None:
    return repr(o) if o else None


#


def fields_dict(cls_or_instance: ta.Any) -> dict[str, dc.Field]:
    return {f.name: f for f in dc.fields(cls_or_instance)}


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


def update_class_metadata(cls: type[T], *args: ta.Any) -> type[T]:
    check.isinstance(cls, type)
    setattr(cls, METADATA_ATTR, md := getattr(cls, METADATA_ATTR, {}))
    md.setdefault(UserMetadata, []).extend(args)
    return cls


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


def update_fields(
        fn: ta.Callable[[str, dc.Field], dc.Field],
        fields: ta.Iterable[str] | None = None,
) -> ta.Callable[[type[T]], type[T]]:
    def inner(cls):
        if fields is None:
            for a, v in list(cls.__dict__.items()):
                if isinstance(v, dc.Field):
                    setattr(cls, a, fn(a, v))

        else:
            for a in fields:
                try:
                    v = cls.__dict__[a]
                except KeyError:
                    v = dc.field()
                else:
                    if not isinstance(v, dc.Field):
                        v = dc.field(default=v)
                setattr(cls, a, fn(a, v))

        return cls

    check.not_isinstance(fields, str)
    return inner


def update_fields_metadata(
        nmd: ta.Mapping,
        fields: ta.Iterable[str] | None = None,
) -> ta.Callable[[type[T]], type[T]]:
    def inner(a: str, f: dc.Field) -> dc.Field:
        return update_field_metadata(f, nmd)

    return update_fields(inner, fields)


#


def deep_replace(o: T, *args: str | ta.Callable[[ta.Any], ta.Mapping[str, ta.Any]]) -> T:
    if not args:
        return o
    elif len(args) == 1:
        return dc.replace(o, **args[0](o))  # type: ignore
    else:
        return dc.replace(o, **{args[0]: deep_replace(getattr(o, args[0]), *args[1:])})  # type: ignore
