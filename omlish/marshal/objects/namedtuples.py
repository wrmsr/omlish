import inspect
import typing as ta

from ... import check
from ... import collections as col
from ... import lang
from ... import reflect as rfl
from ..base import MarshalContext
from ..base import Marshaler
from ..base import Option
from ..base import SimpleMarshalerFactory
from ..base import SimpleUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import Unmarshaler
from .marshal import ObjectMarshaler
from .metadata import FieldInfo
from .metadata import FieldInfos
from .metadata import FieldMetadata
from .unmarshal import ObjectUnmarshaler


##


def _is_namedtuple(rty: rfl.Type) -> bool:
    return (
        isinstance(rty, type) and
        issubclass(rty, tuple) and
        ta.NamedTuple in rfl.get_orig_bases(rty)
    )


def get_namedtuple_field_infos(
        ty: type,
        opts: col.TypeMap[Option] = col.TypeMap(),
) -> FieldInfos:
    check.arg(_is_namedtuple(ty), ty)

    sig = inspect.signature(ty)

    ret: list[FieldInfo] = []
    for param in sig.parameters.values():
        ret.append(FieldInfo(
            name=param.name,
            type=param.annotation,
            metadata=FieldMetadata(),

            marshal_name=param.name,
            unmarshal_names=[param.name],
        ))

    return FieldInfos(ret)


##


class NamedtupleMarshalerFactory(SimpleMarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return _is_namedtuple(rty)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        check.state(_is_namedtuple(rty))
        ty = check.isinstance(rty, type)
        check.state(not lang.is_abstract_class(ty))

        fis = get_namedtuple_field_infos(ty, ctx.options)

        fields = [
            (fi, ctx.make(fi.type))
            for fi in fis
        ]

        return ObjectMarshaler(
            fields,
        )


##


class NamedtupleUnmarshalerFactory(SimpleUnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return _is_namedtuple(rty)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        check.state(_is_namedtuple(rty))
        ty = check.isinstance(rty, type)
        check.state(not lang.is_abstract_class(ty))

        fis = get_namedtuple_field_infos(ty, ctx.options)

        d: dict[str, tuple[FieldInfo, Unmarshaler]] = {}
        defaults: dict[str, ta.Any] = {}

        for fi in fis:
            tup = (fi, ctx.make(fi.type))

            for un in fi.unmarshal_names:
                if un in d:
                    raise KeyError(f'Duplicate fields for name {un!r}: {fi.name!r}, {d[un][0].name!r}')
                d[un] = tup

            if fi.options.default.present:
                defaults[fi.name] = fi.options.default.must()

        return ObjectUnmarshaler(
            ty,
            d,
            defaults=defaults,
        )
