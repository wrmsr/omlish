"""
NOTE: This cannot be auto-imported as @omlish-lite usage of other modules in this package requires it be importable on
8.
"""
import dataclasses as dc
import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs

from .requires import RequiresMarkerItem
from .requires import RequiresMarkerList
from .requires import RequiresNode
from .requires import RequiresOp
from .requires import RequiresValue
from .requires import RequiresVariable


##


class MarshalRequiresMarkerList(lang.NotInstantiable, lang.Final):
    pass


@dc.dataclass(frozen=True)
class RequiresMarkerListMarshaler(msh.Marshaler):
    item_m: msh.Marshaler
    node_m: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        def inner(c: ta.Any) -> ta.Any:
            if isinstance(c, str):
                return c
            elif isinstance(c, RequiresMarkerItem):
                return self.item_m.marshal(ctx, c)
            elif isinstance(c, ta.Iterable):
                return [inner(e) for e in c]
            else:
                raise TypeError(c)
        return [inner(e) for e in o]


class RequiresMarkerListMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalRequiresMarkerList)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return RequiresMarkerListMarshaler(
            ctx.make(RequiresMarkerItem),
            ctx.make(RequiresNode),
        )


##


@lang.static_init
def _install_standard_marshalling() -> None:
    requires_node_poly = msh.Polymorphism(
        RequiresNode,
        [
            msh.Impl(RequiresVariable, 'variable'),
            msh.Impl(RequiresValue, 'value'),
            msh.Impl(RequiresOp, 'op'),
        ],
    )
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
        msh.PolymorphismMarshalerFactory(requires_node_poly),
        msh.PolymorphismUnionMarshalerFactory(requires_node_poly.impls, allow_partial=True),
        RequiresMarkerListMarshalerFactory(),

    ]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
        msh.PolymorphismUnmarshalerFactory(requires_node_poly),
    ]

    msh.GLOBAL_REGISTRY.register(
        RequiresMarkerList,
        msh.ReflectOverride(MarshalRequiresMarkerList),
        identity=True,
    )
