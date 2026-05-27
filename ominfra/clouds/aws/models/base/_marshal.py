import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl

from .base import Enum
from .base import Shape
from .base import ShapeInfo


##


class _EnumMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, Enum)):
            return None
        return lambda: msh.EnumValueMarshaler(rty)


class _EnumUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (isinstance(rty, type) and issubclass(rty, Enum)):
            return None
        return lambda: msh.EnumValueUnmarshaler(rty)


##


def _build_shape_filed_infos(si: ShapeInfo) -> msh.FieldInfos:
    ret: list[msh.FieldInfo] = []

    for sn, fi in si.fields_by_member_name.items():
        ret.append(msh.FieldInfo(
            name=fi.name,
            type=fi.type,
            marshal_name=sn,
            unmarshal_names=[sn],
            options=msh.FieldOptions(
                omit_if=lang.is_none,
            ),
        ))

    return msh.FieldInfos(ret)


#


class _ShapeMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (isinstance(rty, type) and issubclass(sty := rty, Shape)):
            return None

        si: ShapeInfo = sty.__shape__
        fis = _build_shape_filed_infos(si)

        return lambda: msh.ObjectMarshaler([
            (fi, ctx.make_marshaler(fi.type))
            for fi in fis
        ])


#


class _ShapeUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (isinstance(rty, type) and issubclass(sty := rty, Shape)):
            return None

        si: ShapeInfo = sty.__shape__
        fis = _build_shape_filed_infos(si)

        return lambda: msh.ObjectUnmarshaler(
            sty,
            {
                check.non_empty_str(fi.marshal_name): (fi, ctx.make_unmarshaler(fi.type))
                for fi in fis
            },
        )


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories(
        cfgs,

        _EnumMarshalerFactory(),
        _EnumUnmarshalerFactory(),

        _ShapeMarshalerFactory(),
        _ShapeUnmarshalerFactory(),
    )
