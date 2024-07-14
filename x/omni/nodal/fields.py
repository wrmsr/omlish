"""
Note: These are explicitly usable by nodal-'like' but not actually nodal classes.
"""
import collections.abc
import types
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import reflect as rfl
from .types import IGNORE


T = ta.TypeVar('T')
StrMap = ta.Mapping[str, ta.Any]


class Field(dc.Pure):
    name: str
    spec: rfl.TypeSpec
    opt: bool = False
    seq: bool = False
    peer: bool = False

    @property
    def cls(self) -> type:
        return self.spec.erased_cls

    @classmethod
    def build(
            cls,
            obj: ta.Union['Field', dc.Field],
            *,
            root_cls: ta.Optional[type] = None,
            type_hints: ta.Optional[StrMap] = None,
    ) -> ta.Optional['Field']:
        if isinstance(obj, Field):
            return obj

        elif isinstance(obj, dc.Field):
            if obj.metadata.get(IGNORE):
                return None

            if type_hints is not None:
                ty = type_hints[obj.name]
            else:
                ty = obj.type

            fs = rfl.spec(ty)
            opt = False
            seq = False
            peer = False

            if isinstance(fs, rfl.UnionSpec) and fs.optional_arg is not None:
                fs = fs.optional_arg
                opt = True

            if isinstance(fs, rfl.SpecialParameterizedGenericTypeSpec) and fs.erased_cls is collections.abc.Sequence:
                [fs] = fs.args
                seq = True

            if root_cls is not None:
                if isinstance(fs, rfl.TypeSpec) and issubclass(fs.erased_cls, root_cls):
                    peer = True

                else:
                    def flatten(s):
                        yield s
                        if isinstance(s, (rfl.UnionSpec, rfl.GenericTypeSpec)):
                            for a in s.args:
                                yield from flatten(a)

                    l = list(flatten(fs))
                    if any(isinstance(e, rfl.TypeSpec) and issubclass(e.erased_cls, root_cls) for e in l):
                        raise TypeError(f'Peer fields must be simple (optional sequences): {obj.name} {fs}')

            if not isinstance(fs, rfl.TypeSpec):
                return None

            return Field(
                name=obj.name,
                spec=fs,
                opt=opt,
                seq=seq,
                peer=peer,
            )

        else:
            raise TypeError(obj)


class Fields(dc.Pure):
    flds: ta.Mapping[str, Field]


def build_nodal_fields(
        cls: type,
        root_cls: type,
        *,
        peers_only: bool = False,
        strict: bool = False,
) -> Fields:
    check.arg(isinstance(cls, type) and dc.is_dataclass(cls))
    check.issubclass(cls, root_cls)

    th = ta.get_type_hints(cls)
    flds = {}

    for f in dc.fields(cls):
        if f.metadata.get(IGNORE):
            continue

        fi = Field.build(f, root_cls=root_cls, type_hints=th)

        if fi is None:
            if strict:
                raise TypeError(f)

        elif fi.peer or not peers_only:
            flds[f.name] = fi

    return Fields(flds)


def check_nodal_field_value(v: T, f: Field) -> T:
    if f.opt and v is None:
        pass

    elif v is None:
        raise TypeError(v, f)

    elif f.seq:
        if isinstance(v, (types.GeneratorType, str)):
            raise TypeError(v, f)

        if not isinstance(v, ta.Sequence):
            raise TypeError(v, f)

        for e in v:
            if not isinstance(e, f.cls):
                raise TypeError(e, f)

    else:
        if not isinstance(v, f.cls):
            raise TypeError(v, f)

    return v


def check_nodal_fields(obj: ta.Any, fi: Fields) -> None:
    for a, f in fi.flds.items():
        v = getattr(obj, a)
        check_nodal_field_value(v, f)
