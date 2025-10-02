import inspect
import typing as ta

from ... import check
from ... import collections as col
from ... import lang
from ... import reflect as rfl
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.options import Option
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
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


class NamedtupleMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not _is_namedtuple(rty):
            return None

        def inner() -> Marshaler:
            check.state(_is_namedtuple(rty))
            ty = check.isinstance(rty, type)
            check.state(not lang.is_abstract_class(ty))

            fis = get_namedtuple_field_infos(ty, ctx.options)

            fields = [
                (fi, ctx.make_marshaler(fi.type))
                for fi in fis
            ]

            return ObjectMarshaler(
                fields,
            )

        return inner


##


class NamedtupleUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not _is_namedtuple(rty):
            return None

        def inner() -> Unmarshaler:
            check.state(_is_namedtuple(rty))
            ty = check.isinstance(rty, type)
            check.state(not lang.is_abstract_class(ty))

            fis = get_namedtuple_field_infos(ty, ctx.options)

            d: dict[str, tuple[FieldInfo, Unmarshaler]] = {}
            defaults: dict[str, ta.Any] = {}

            for fi in fis:
                tup = (fi, ctx.make_unmarshaler(fi.type))

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

        return inner
