import inspect
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .infos import FieldInfo
from .infos import FieldInfos
from .marshal import ObjectMarshaler
from .unmarshal import ObjectUnmarshaler


##


def _get_namedtuple_cls(rty: rfl.Type) -> type | None:
    if (
            isinstance(rty, rfl.Instance) and
            (cls := rfl.get_runtime_type_or_none(rty)) is not None and
            issubclass(cls, tuple) and
            ta.NamedTuple in rfl.get_orig_bases(cls)
    ):
        return cls
    return None


def _is_namedtuple_cls(ty: type) -> bool:
    return issubclass(ty, tuple) and ta.NamedTuple in rfl.get_orig_bases(ty)


def get_namedtuple_field_infos(ty: type) -> FieldInfos:
    check.arg(_is_namedtuple_cls(ty), ty)

    sig = inspect.signature(ty)

    ret: list[FieldInfo] = []
    for param in sig.parameters.values():
        ret.append(FieldInfo(
            name=param.name,
            type=param.annotation,

            marshal_name=param.name,
            unmarshal_names=[param.name],
        ))

    return FieldInfos(ret)


##


class NamedtupleMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (cls := _get_namedtuple_cls(rty)) is None:
            return None

        def inner() -> Marshaler:
            ty = check.not_none(cls)
            check.state(not lang.is_abstract_class(ty))

            fis = get_namedtuple_field_infos(ty)

            fields = [
                (fi, ctx.make_marshaler(fi.type))
                for fi in fis
                if not fi.options.no_marshal
            ]

            return ObjectMarshaler(
                fields,
            )

        return inner


##


class NamedtupleUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (cls := _get_namedtuple_cls(rty)) is None:
            return None

        def inner() -> Unmarshaler:
            ty = check.not_none(cls)
            check.state(not lang.is_abstract_class(ty))

            fis = get_namedtuple_field_infos(ty)

            d: dict[str, tuple[FieldInfo, Unmarshaler]] = {}
            defaults: dict[str, ta.Any] = {}

            for fi in fis:
                if fi.options.no_unmarshal:
                    continue

                tup = (fi, ctx.make_unmarshaler(fi.type))

                for un in fi.unmarshal_names:
                    if un in d:
                        raise KeyError(f'Duplicate fields for name {un!r}: {fi.name!r}, {d[un][0].name!r}')
                    d[un] = tup

                if (dfl := fi.options.default) is not None and dfl.present:
                    defaults[fi.name] = dfl.must()

            return ObjectUnmarshaler(
                ty,
                d,
                defaults=defaults,
            )

        return inner
